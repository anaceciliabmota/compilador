var texto_falso: bool = true;
var um_numero: int = 42;

fun sub(a: int, b: int) -> int {
    return a - b;
}

main {
    # Isso deve emitir um erro semântico reportando falta de tipagem estrita
    var x: int = sub(um_numero, texto_falso);
   
    return x;
}
