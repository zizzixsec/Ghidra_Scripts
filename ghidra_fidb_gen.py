#!/usr/bin/env python3
from os import getenv
from sys import exit
from argparse import ArgumentParser
from pathlib import Path
from urllib.request import urlopen
from shutil import copyfileobj, copy
from re import compile
from tempfile import TemporaryDirectory
from subprocess import run

def die(msg):
    exit(f"[!] - {msg}")

class FIDBIMPORTER:
    def __init__(self, args):
        self.file = args.file
        self.distro = self.file.split('.')[0]
        self.lib_folder = Path("lib/")
        self.src_folder = Path("src/")
        self.log_folder = Path("log/")
        self.fidb_folder = Path("fidb/")
        self.ghidra_home = Path(getenv("GHIDRA_HOME"))
        self.ghidra_proj = Path(getenv("GHIDRA_PROJ"))
        self.ghidra_headless = self.ghidra_home / "support" / "analyzeHeadless"
        self.common_log = self.log_folder / f"{self.distro}-common.txt"
        self.headless_log = self.log_folder / f"{self.distro}-headless.log"
        self.langids_log = self.log_folder / f"{self.distro}-langids.txt"
        self.duplicate_log = self.log_folder / "duplicate_results.txt"
        self.zip_log = self.log_folder / "7z.log"
        self.proj_name = "lib-fidb"

    def get_srcs(self, path):
        print("[*] - Downloading source files...")
        if not Path(self.file).is_file():
            die(f"File {self.file} not found")
        with open(self.file, "r") as f:
            urls = [x.rstrip() for x in f.readlines()]
        
        path.mkdir(parents=True, exist_ok=True)

        for url in urls:
            fn = path / url.split('/')[-1]
            if not fn.is_file():
                with urlopen(url) as r, open(fn, 'wb') as f:
                    copyfileobj(r, f)

    def extract_debs(self, path, dist):
        print(f"[*] - Extracting {dist} files...")
        name_pattern = compile(r'^(.*)-([^-]+)-(.+)\.deb$')
        for debfile in path.iterdir():
            pkg = debfile.name.split('/')[-1]
            m = name_pattern.match(pkg)
            name = m.group(1)
            version = m.group(2)
            release = f"{m.group(3)}"
            
            dest = self.lib_folder / dist / name / version / release
            dest.mkdir(parents=True, exist_ok=True)

            with TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                pkgpath = tmppath / pkg
                copy(str(debfile), str(pkgpath))
                run(["ar", "x", pkgpath, "--output", tmppath])
                for f in tmppath.iterdir():
                    if f.is_file() and f.name.startswith("data.tar"):
                        run(["tar", "-xf", f, "-C", tmppath])
                for a in (tmppath / "usr").rglob("*"):
                    if a.is_file() and a.name.endswith(".a"):
                        copy(str(a.absolute()), str(dest / a.name))

    def unpack_libs(self):
        print("[*] - Unpacking libraries...")

        with open(self.zip_log, "w") as outfile:
            for lib in self.lib_folder.rglob("*"):
                if lib.is_file() and lib.name.endswith(".a"):
                    libpath = Path(str(lib)[:-2])
                    libpath.mkdir(parents=True, exist_ok=True)
                    run(["7z", "-y", "x", lib, f"-o{str(libpath)}"], stdout=outfile, stderr=outfile)

        tmpData = []
        
        for obj in (self.lib_folder / self.distro).rglob(f"*"):
            if obj.is_file():
                if obj.name.endswith(".txt"):
                    with open(obj, "r") as infile:
                        for line in infile.readlines():
                            tmpData.append(line.split()[1].rstrip())

                if not obj.name.endswith(".o") and not obj.name.endswith(".obj"):
                        obj.unlink(missing_ok=True)
                elif obj.is_symlink():
                    obj.unlink(missing_ok=True)

        with open(self.common_log, "w") as outfile:
            for item in set(tmpData):  
                outfile.write(f"{item}\n")


    def ghidra_import(self):
        print("[*] - Running Ghidra Headless Analyzer...")
        print(f"[i] - Run `tail -f {self.headless_log}` for status...")

        with open(self.headless_log, "w") as outfile:
            run([self.ghidra_headless, self.ghidra_proj, self.proj_name, "-import", self.lib_folder, \
                "-recursive", "-scriptPath", "ghidra_scripts", "-preScript", \
                    "FunctionIDHeadlessPrescriptMinimal.java", "-postScript", \
                        "FunctionIDHeadlessPostscript.java"], stdout=outfile, stderr=outfile)

    def generate_langids(self):
        print("[*] - Generating Language IDs...")
        langid_pattern = compile(r'\b(\w+:\w+:\w+:\w+:\w+)\b')

        tmpData = []
        with open(self.headless_log, "r") as infile:
            for line in infile.readlines():
                m = langid_pattern.search(line)
                if m:
                    tmpData.append(m.group(1).rstrip())
        
        with open(self.langids_log, "w") as outfile:
            for item in set(tmpData):
                outfile.write(f"{item}\n")

    def generate_fidb(self):
        print("[*] - Generating FIDBs...")
        self.duplicate_log.touch(exist_ok=True)

        with open(self.langids_log, "r") as log:
            for langid in set(log.readlines()):
                langid_dots = langid.replace(':','.')
                run([self.ghidra_headless, self.ghidra_proj, self.proj_name, "-noanalysis", \
                    "-scriptPath", "ghidra_scripts", "-preScript", "AutoCreateMultipleLibraries.java", \
                        self.duplicate_log, "true", "fidb", f"{self.distro}-{langid_dots}.fidb", \
                            f"{self.lib_folder}/{self.distro}", f"log/{self.distro}-common.txt", langid])

    def importer(self):
        self.lib_folder.mkdir(parents=True, exist_ok=True)
        self.src_folder.mkdir(parents=True, exist_ok=True)
        self.log_folder.mkdir(parents=True, exist_ok=True)
        self.fidb_folder.mkdir(parents=True, exist_ok=True)

        if self.file.endswith('.txt'):
            _path = self.src_folder / ".".join(self.file.split(".")[:-1])
        else:
            _path = self.src_folder / self.file

        self.get_srcs(_path)
        self.extract_debs(_path, self.distro)
        self.unpack_libs()
        self.ghidra_import()
        self.generate_langids()
        # self.generate_fidb()


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', action='store', required=True, help='library URLs to load')
    return parser.parse_args()

def main():
    print("[*] - Starting FIDB importer...")
    if not getenv('GHIDRA_HOME') or not getenv('GHIDRA_PROJ'):
        die("GHIDRA_HOME or GHIDRA_PROJ environment variables not set")
    
    fidbimporter = FIDBIMPORTER(get_args())
    fidbimporter.importer()
    print("[*] - FIDB importer complete!")

if __name__ == "__main__":
    main()
