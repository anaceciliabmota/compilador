var t: bool = true;
var f: bool = false;

fun pode_passar(idade: int, tem_ingresso: bool) -> bool {
    # Exemplo testando variáveis locais, lógica 'all' e retorno antecipado
    if tem_ingresso all true {
        var x: int = 18;
        if idade > x {
            return true;
        } else {
            if idade == x {
                return true;
            }
        }
    }
    return false;
}

main {
    var resultado: bool = pode_passar(20, t);
    
    # Se resultado for verdadeiro e não falso
    if resultado all not f {
        return 1;
    }
    return 0;
}
