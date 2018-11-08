'''

'''

comandos = {
    "lose_life" : {
        "tipo" : "automatico",
        "comando" : "command_lose_life",
        "argumentos" : None
    },
    "gain_food" : {
        "tipo" : "automatico",
        "comando" : "command_gainfood",
        "argumentos" : None
    },
    "remove_rute" : {
        "tipo" : "automatico", #Comandos con automatico se hacen sin preguntar nada al usuario
        "comando" : "command_remove_exploration",
        "argumentos" : []
    },
    "gain_skill" : {
        "tipo" : "final", # Comandos con final se ejecutan al terminar de resolver.
        "comando" : "command_gain_skill",
        "argumentos" : []
    },
    "gain_bullet" : {
        "tipo" : "automatico",
        "comando" : "gainbullet",
        "argumentos" : None
    },
    "swap_rute" : {
        "tipo" : "opcional", # Comandos opcional se preguntara si el usuario quiere hacerlo
        "comando" : "command_swap_exploration",
        "argumentos" : None
    }
}

cartas_aventura = {
    0.5 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "0",
        "columna" : "0",
        "actions" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "gain_food",
                            3 : "gain_food"                           
                        }
                    }
                }
            },
            2 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "remove_exploration",
                            2 : "remove_exploration",
                            3 : "remove_exploration",                            
                        }
                    }
                }            
            }
        }
    },
    1 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "0",
        "columna" : "1",
        "actions" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "gain_skill"                            
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "remove_rute"                           
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "gain_skill"                          
                        }
                    }
                }
            }
        }
    },
    2 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "0",
        "columna" : "2",
        "actions" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : "gain_skill",
                    2 : "gain_bullet"
                }
            }
        }
    },
    3 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "1",
        "columna" : "0",
        "actions" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "gain_food"                          
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "gain_food",
                            3 : "gain_food"                           
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "gain_food",
                            3 : "gain_food"                           
                        }
                    }
                }
            }
        }
    },
    4 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "1",
        "columna" : "1"      
    },
    5 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "1",
        "columna" : "2"     
    },
    6 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "2",
        "columna" : "0"
    },
    7 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "2",
        "columna" : "1"
    },
    8 : {
        "nombre" : "Nombre",
        "plastilla" : "1",
        "fila" : "2",
        "columna" : "2"
    },
    9 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "0",
        "columna" : "0"
        
    },
    10 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "0",
        "columna" : "1"
    },
    10.5 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "0",
        "columna" : "2"
    },
    11 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "1",
        "columna" : "0"
    },
    12 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "1",
        "columna" : "1"
    },
    13 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "1",
        "columna" : "2"
    },
    14 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "2",
        "columna" : "0"
    },
    15 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "2",
        "columna" : "1"
    },
    16 : {
        "nombre" : "Nombre",
        "plastilla" : "2",
        "fila" : "2",
        "columna" : "2"
    },
    17 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "0",
        "columna" : "0"
    },
    18 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "0", 
        "columna" : "1"
    },
    19 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "0",
        "columna" : "2"
    },
    20 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "1", 
        "columna" : "0"
    },
    20.5 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "1", 
        "columna" : "1"
    },
    21 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "1",
        "columna" : "2"
    },
    22 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "2",
        "columna" : "0"
    },
    23 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "2", 
        "columna" : "1"
    },
    24 : {
        "nombre" : "Nombre",
        "plastilla" : "3",
        "fila" : "2", 
        "columna" : "2"
    },
    25 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "0",
        "columna" : "0"
        
    },
    26 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "0",
        "columna" : "1"
    },
    27 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "0",
        "columna" : "2"
    },
    28 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "1",
        "columna" : "0"
    },
    29 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "1",
        "columna" : "1"
    },
    30 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "1",
        "columna" : "2"
    },
    31 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "2",
        "columna" : "0"
    },
    32 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "2",
        "columna" : "1"
    },
    33 : {
        "nombre" : "Nombre",
        "plastilla" : "4",
        "fila" : "2",
        "columna" : "2"
    },
    34 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "0",
        "columna" : "0"
        
    },
    35 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "0",
        "columna" : "1"
    },
    36 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "0",
        "columna" : "2"
    },
    37 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "1",
        "columna" : "0"
    },
    38 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "1",
        "columna" : "1"
    },
    39 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "1",
        "columna" : "2"
    },
    40 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "2",
        "columna" : "0"
    },
    40.5 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "2",
        "columna" : "1"
    },
    41 : {
        "nombre" : "Nombre",
        "plastilla" : "5",
        "fila" : "2",
        "columna" : "2"
    },
    42 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "0",
        "columna" : "0"
        
    },
    43 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "0",
        "columna" : "1"
    },
    44 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "0", 
        "columna" : "2"
    },
    45 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "1", 
        "columna" : "0"
    },
    46 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "1", 
        "columna" : "1"
    },
    47 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "1", 
        "columna" : "2"
    },
    48 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "2", 
        "columna" : "0"
    },
    49 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "2", 
        "columna" : "1"
    },
    50 : {
        "nombre" : "Nombre",
        "plastilla" : "6",
        "fila" : "2", 
        "columna" : "2"
    },
    50.5 : {
        "nombre" : "Nombre",
        "plastilla" : "7",
        "fila" : "0", 
        "columna" : "0"
        
    },
    51 : {
        "nombre" : "Nombre",
        "plastilla" : "7",
        "fila" : "0", 
        "columna" : "1"
    },
    52 : {
        "nombre" : "Nombre",
        "plastilla" : "7",
        "fila" : "0", 
        "columna" : "2"   
    },
    53 : {
        "nombre" : "Nombre",
        "plastilla" : "7",
        "fila" : "1", 
        "columna" : "0"    
    },
    54 : {
        "nombre" : "Nombre",
        "plastilla" : "7",
        "fila" : "1", 
        "columna" : "1"     
    },
    55 : {
        "nombre" : "Nombre",
        "plastilla" : "7",
        "fila" : "1", 
        "columna" : "2"    
    },
    56 : {
        "nombre" : "Nombre",
        "plastilla" : "7",
        "fila" : "2", 
        "columna" : "0"     
    },
    99.5 : {
        "nombre" : "Nombre",
        "plastilla" : "7",
        "fila" : "2", 
        "columna" : "1"     
    },    
}


actions = {
    "Ver" : {
        "costo" : "2",
        "comando" : "Ver" 
    },
    "Limpiar" : {
        "costo" : "3",
        "comando" : "Limpiar" 
    },
    "Asesinar" : {
        "costo" : "Mitad +1",
        "comando" : "Asesinar" 
    },
    "Exorcisar" : {
        "costo" : "Cantidad de jugadores investigadores",
        "comando" : "Exorcisar" 
    }
}

playerSets = {
    # only for testing purposes
    
    5: {
        "roles": [
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Cultista"
        ],
        "track": [
            None,
            None,
            "policy",
            "kill",
            "kill",
            "win"
        ]
    },
    6: {
        "roles": [
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Cultista",
            "Cultista"
        ],
        "track": [
            None,
            None,
            "policy",
            "kill",
            "kill",
            "win"
        ]
    },
    7: {
        "roles": [
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Cultista",
            "Cultista"
        ],
        "track": [
            None,
            "inspect",
            "choose",
            "kill",
            "kill",
            "win"
        ]
    },
    8: {
        "roles": [
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Cultista",
            "Cultista"
        ],
        "track": [
            None,
            "inspect",
            "choose",
            "kill",
            "kill",
            "win"
        ]
    },
    9: {
        "roles": [
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Investigador",
            "Cultista",
            "Cultista",
            "Cultista"
        ],
        "track": [
            "inspect",
            "inspect",
            "choose",
            "kill",
            "kill",
            "win"
        ]
    },
}

policies = [
        "liberal",
        "liberal",
        "liberal",
        "liberal",
        "liberal",
        "liberal",
        "fascist",
        "fascist",
        "fascist",
        "fascist",
        "fascist",
        "fascist",
        "fascist",
        "fascist",
        "fascist",
        "fascist",
        "fascist"
    ]
