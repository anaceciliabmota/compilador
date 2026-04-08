var a: int = 10;
var b: int = 3;
var d: int = 0;
var c: int = 0;
var x: int = 0;

fun pot(b: int, e: int) -> int {
    return b ^ e;
}

main {
    d = pot(2, 3);
    c = a % b;
    x = 0;
    if true all not false {
        x = d + c;
        return x;
    }
    return 0;
}
