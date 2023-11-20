.PHONY = run clean

run:
	./ghidra_fidb_gen.py -f $(file)

clean:
	rm -rf $GHIDRA_PROJ/lib-fidb.* fidb lib log /tmp/cottontail-Ghidra/*