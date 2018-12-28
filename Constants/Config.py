TOKEN = "PUT HERE TOKEN OR IN DB"
ADMIN = [387393551, 441820689, 445782140] #your telegram ID
#Leviatas Ale Cadogan
STATS = "../stats.json"

JUEGOS_DISPONIBLES = {        
        "LostExpedition" : {
                "comandos" : {
                    "LostExpedition" : "Lost Expedition"
                },
                "restriccion" : "admin",                
        },
        "JustOne" : {
                "comandos" : {
                    "JustOne" : "Just One"
                },
		"permitir_ingreso_tardio" : True
        },
        "SistemaD100" : {
                "comandos" : {
                    "SistemaD100" : "SistemaD100"
                },
                "permitir_ingreso_tardio" : True
        },
	"HarryPotter" : {
                "comandos" : {
                    "HarryPotter" : "Harry Potter"
                },
		"restriccion" : "admin",
                "permitir_ingreso_tardio" : True
        },
	"SayAnything" : {
                "comandos" : {
                    "SayAnything" : "Say Anything"
                },
		"restriccion" : "admin",
                "permitir_ingreso_tardio" : True
        }
}


HOJAS_AYUDA = {
        "JustOne" : "_Pistas no validas:_\n" + \
		"*Pista con más de 1 palabra.* Ej: El Padrino para Don\n" + \
		"*Pista con ortografia diferente.* Ej: Kamiza para Camisa\n" + \
		"*Palabras escritas en otro idioma.* Ej:Black para Negro\n"  + \
		"*Una palabra de la misma familia* Ej:Principe para Princesa\n"  + \
		"*Una palabra inventada* Ej:Cositadulz para Pastel\n"  + \
		"*Una palabra foneticamente identica.* Ej: Tuvo para Tubo\n" + \
		"Pistas *identicas*\n" + \
		"_Dos palabras identicas._\n" + \
		"*Variantes de una misma familia de palabras* Ej: Princesa y Principe\n" + \
		"*Las variantes de una misma palabra: los plurales, diferencias de genero" + \
		" y faltas de ortografia no cuenta como diferencias reales* Ej: Principe y Principes, " + \
		"Panadero y Panadera, Tobogán y Tovogan son identicas.",	
        "LostExpedition" : "Eventos amarillos son obligatorios\n" + \
		"Eventos rojo son obligatorios pero tenes que elegir 1\n"  + \
		"Eventos Azules son opcionales"        
}

MODULOS_DISPONIBES = {        
        "LostExpedition" : {
                "Solitario" : {
                        "comandos" : {
                            "Solitario" : "Solitario"
                        },
                        "min_jugadores" : 1,
                        "max_jugadores" : 1
                },
                "Cooperativo" : {                        
                        "comandos" : {
                            "Cooperativo" : "Cooperativo"
                        },
                        "min_jugadores" : 2,
                        "max_jugadores" : 5
                },
                "Competitivo" : {                        
                        "comandos" : {
                            "Competitivo" : "Competitivo"
                        },
                        "min_jugadores" : 2,
                        "max_jugadores" : 2
                } 
        },
        "JustOne" : {
                "Cooperativo" : {
                        "comandos" : {
                            "Cooperativo" : "Cooperativo"
                        },
                        "min_jugadores" : 1,
                        "max_jugadores" : 7
                } 
        },
	"SayAnything" : {
                "Cooperativo" : {
                        "comandos" : {
                            "Cooperativo" : "Cooperativo"
                        },
                        "min_jugadores" : 1,
                        "max_jugadores" : 8
                } 
        },
        "SistemaD100" : {
                "Cooperativo" : {
                        "comandos" : {
                            "Cooperativo" : "Cooperativo"
                        },
                        "min_jugadores" : 1,
                        "max_jugadores" : 99
                } 
        }
}
