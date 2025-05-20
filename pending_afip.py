from db import with_db_connection
from decimal import Decimal
from collections import defaultdict


@with_db_connection
def get_recorridos(cursor, conn):
    cursor.execute(
        """
        SELECT * FROM EGALLM.RECORRI
        """
    )
    itiner_records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in itiner_records]

@with_db_connection
def query(cursor, conn):
    cursor.execute(
        """
        SELECT
        AFIPRELA.ALETRAA PREFACTURA_LETRA,
        AFIPRELA.APREFIA PREFACTURA_PREFIJO,
        AFIPRELA.ANROA PREFACTURA_NRO,
        AFIPRELA.APREFIA PUNTO_VENTA,
        AFIPRELA.AGCLIEN CLIENTE,
        FCELEE00.FEFEFC FECHA_EMISION,
        FCELEE00.FEFEVT FECHA_VENCIMIENTO,
        FCELEE00.FEIMTO PRECIO,
        FCELEI00.FEIVIM IVA,
        FCELET00.FETRIM IIBB,
        FCELEI00.FEIVBI BASE_IIBB,
        FACTUMAY.FANEG NEGOCIO,
        FACTUMAY.FACVTA COND_VENTA, -- E CTA CTE
        SUBSTRING(AFIPRELA.AOTROS, 1, 10) IMPRESORA,
        FACTUMAY.FACREC ORIGEN_DESTINO,
        FACTUMAY.FAKGS KILOS,
        FACTUMAY.FALIBRE FLETE,
        FACTUMAY.FASEG1 SEGURO,
        FACTUMAY.FAOTR1 SERV_ADIC,
        FACTUMAY.FAREE1 REEMBOLSO,
        -FACTUMAY.FAIVAX BONIFICACION,
        FACTUMAY.FASIVA1 IMPORT_ITEM
        FROM TEST.FACTUMAY FACTUMAY
        JOIN TEST.AFIPRELA AFIPRELA
          ON FACTUMAY.FALET = AFIPRELA.ALETRAA AND FACTUMAY.FAPRE = AFIPRELA.APREFIA AND FACTUMAY.FANRO = AFIPRELA.ANROA
        JOIN TEST.FCELEE00 FCELEE00
          ON AFIPRELA.AFESOSE = FCELEE00.FESOSE
        LEFT JOIN TEST.FCELET00 FCELET00
          ON FCELEE00.FESOSE = FCELET00.FESOSE AND FCELET00.FEEMPR = 'EL'
        LEFT JOIN TEST.FCELEI00 FCELEI00
          ON FCELEE00.FESOSE = FCELEI00.FESOSE AND FCELEI00.FEEMPR = 'EL'
        WHERE
        FCELEE00.FEEMPR = 'EL' AND
        FACTUMAY.FALET = 'A' AND
        -- DISTRIBUCION
        --FACTUMAY.FAPRE = 1021 AND
        --FACTUMAY.FANRO = 46306 -- 46362
        --FACTUMAY.FAPRE = 1051 AND
        --FACTUMAY.FANRO = 2443

        -- LARGA DISTANCIA
        --FACTUMAY.FAPRE = 1001 AND
        --FACTUMAY.FANRO = 158715
        -- ENCOMIENDA CON 3 ENVIOS
        --FACTUMAY.FAPRE = 1051 AND
        --FACTUMAY.FANRO = 1374
        -- CON REEMBOLSO
        --FACTUMAY.FAPRE = 1001 AND
        --FACTUMAY.FANRO = 114393
        -- ENCOMIENDA CON BONIFICACION
        FACTUMAY.FAPRE = 1031 AND
        FACTUMAY.FANRO = 81966
        ORDER BY AFESOSE DESC
        FETCH FIRST 10 ROWS ONLY
        """
    )
    itiner_records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in itiner_records]


@with_db_connection
def agrupar_prefacturas(cursor, conn):
    recorridos = get_recorridos(cursor, conn)
    recorridos_dict = {item['IDREC']: item['DESREC'].strip() for item in recorridos}
    registros = query(cursor, conn)
    registros = [{k.lower(): v for k, v in r.items()} for r in registros]

    campos_comunes = [
        'prefactura_letra', 'prefactura_prefijo', 'prefactura_nro', 'punto_venta', 'cliente',
        'fecha_emision', 'fecha_vencimiento', 'precio', 'iva', 'iibb', 'base_iibb',
        'negocio', 'cond_venta', 'impresora'
    ]

    conceptos_legibles = {
        'flete': 'Flete',
        'serv_adic': 'Servicio adicional',
        'reembolso': 'Reembolso',
        'bonificacion': 'Bonificación'
    }

    agrupado = defaultdict(list)
    for registro in registros:
        clave = tuple(registro.get(k) for k in campos_comunes)
        origen_destino = registro.get('origen_destino')
        descripcion_base = 'Rec.: ' + recorridos_dict.get(origen_destino, '')

        auxiliares = list(origen_destino) if origen_destino and len(origen_destino) == 2 else []
        negocio = registro.get('negocio', '').strip().upper()
        sufijo = '-encomiendas' if negocio == 'E' else '-distribucion'

        for campo in conceptos_legibles:
            valor = registro.get(campo)
            if valor is not None and valor != 0:
                descripcion = f"{conceptos_legibles[campo]} - {descripcion_base}"
                if campo == 'flete':
                    kilos = registro.get('kilos')
                    if kilos:
                        descripcion += f" - Kilos: {kilos:.2f}"
                item = {
                    'tipo': f"{campo}{sufijo}",
                    'origen_destino': origen_destino,
                    'importe': valor,
                    'descripcion': descripcion,
                    'auxiliares': auxiliares
                }
                agrupado[clave].append(item)

    resultado = []
    for clave, items in agrupado.items():
        cabecera = dict(zip(campos_comunes, clave))
        cabecera["items"] = items
        resultado.append(cabecera)

    return resultado
