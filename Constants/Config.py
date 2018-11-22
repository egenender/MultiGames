TOKEN = "501280363:AAGr5YOn5-HBAKOKJoSSUys6NOfUC-A9PwM"
ADMIN = [387393551, 441820689, 445782140] #your telegram ID
#Leviatas Ale Cadogan
STATS = "../stats.json"

JUEGOS_DISPONIBLES = {        
        "LostExpedition" : {
                "comandos" : {
                    "LostExpedition" : "Lost Expedition"
                }
        },
        "JustOne" : {
                "comandos" : {
                    "JustOne" : "Just One"
                }
        }
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
                        "min_jugadores" : 2,
                        "max_jugadores" : 8
                } 
        }
}
