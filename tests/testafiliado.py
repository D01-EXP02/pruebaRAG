from src.afiliados.repositorio import AfiliadosRepository, AfiliadoNoEncontradoError

def test_buscar_afiliado_existente():
    repo = AfiliadosRepository("data/afiliados/BD_afiliados.xlsx")
    afiliado = repo.buscar_por_id("A-00001")
    assert afiliado is not None
    assert afiliado.plan == "Esencial"

def test_afiliado_inexistente_retorna_none():
    repo = AfiliadosRepository("data/afiliados/BD_afiliados.xlsx")
    assert repo.buscar_por_id("A-99999") is None