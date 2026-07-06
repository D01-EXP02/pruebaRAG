from src.agent.cli import extraer_id_afiliado


def test_extraer_id_afiliado_desde_consulta():
    consulta = (
        "Por medio del presente escrito, y en mi calidad de afiliado titular al "
        "plan de salud identificado con el número de afiliación A-00427, solicito..."
    )

    assert extraer_id_afiliado(consulta) == "A-00427"
