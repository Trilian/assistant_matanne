import os, sys
R = {
    "\xc3\xb0\xc5\xb8": "\xf0\x9f",
    "\xc3\xa2\xc5\x93\xc2\x85": "\xe2\x9c\x85",
    "\xc3\xa2\xc2\x8c": "\xe2\x8c",
    "\xc3\xa2\xc2\x86\xe2\x80\x99": "\xe2\x86\x92",
    "\xc3\xa2\xc2\x9a\xc2\xa1": "\xe2\x9a\xa1",
    "\xc3\xa2\xc2\xb3": "\xe2\x8f\xb3",
}
c = 0
for r,d,f in os.walk(sys.argv[1] if len(sys.argv)>1 else "src"):
    for n in f:
        if n.endswith(".py"):
            p = os.path.join(r,n)
            with open(p,"r",encoding="utf-8") as fp: t = fp.read()
            o = t
            for old,new in R.items(): t = t.replace(old, new)
            if t != o:
                with open(p,"w",encoding="utf-8") as fp: fp.write(t)
                c += 1
                print(f"Fixed: {p}")
print(f"Total: {c}")