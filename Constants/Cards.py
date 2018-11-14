'''
Crear comandos:
command_lose_camp
command_lose_compass
command_lose_leaf
command_lose_explorer "lose_explorer",
'''

comandos = { 
    "remove_rute" : {
        "tipo" : "automatico", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
        "comando" : "command_remove_exploration",
        "comando_argumentos" : [2]
    },
    "remove_last_rute" : {
        "tipo" : "automatico", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
        "comando" : "command_remove_last_exploration"        
    },
    "add_rute" : {
        "tipo" : "automatico", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
        "comando" : "command_add_exploration_deck",
        "comando_argumentos" : []
    },
    "swap_rute" : {
        "tipo" : "indicaciones",
        "comando" : "command_swap_exploration",
        "indicacion" : "¿Quiere intercambiar dos cartas de ruta?",
        "indicacion_argumentos" : ["Sí", "No"]
    },    
    "gain_life" : {
        "tipo" : "indicaciones",
        "comando" : "command_gain_life",
        "indicacion" : "Elija a un explorador para ganar una vida",
        "indicacion_argumentos" : ["Explorador Campero", "Explorador Brujula", "Explorador Hoja"]
    },
    "gain_skill" : {
        "tipo" : "final", # Comandos con final se ejecutan al terminar de resolver.
        "comando" : "command_gain_skill",
        "comando_argumentos" : []
    },
    "gain_food" : {
        "tipo" : "automatico",
        "comando" : "command_gainfood",        
    },
    "gain_bullet" : {
        "tipo" : "automatico",
        "comando" : "command_gainbullet"
    },
    "gain_progreso" : {
        "tipo" : "automatico",
        "comando" : "command_increase_progreso"
    },
    "lose_camp" : {
        "tipo" : "indicaciones",
        "comando" : "command_lose_camp",
        "indicacion" : "Elija que quiere hacer",
        "indicacion_argumentos" : ["Explorador Campero", "Explorador Brujula", "Explorador Hoja", "Usar carta skill"]
    },
    "lose_leaf" : {
        "tipo" : "indicaciones",
        "comando" : "command_lose_leaf",
        "indicacion" : "Elija que quiere hacer",
        "indicacion_argumentos" : ["Explorador Campero", "Explorador Brujula", "Explorador Hoja", "Usar carta skill"]
    },
    "lose_compass" : {
        "tipo" : "indicaciones",
        "comando" : "command_lose_compass",
        "indicacion" : "Elija que quiere hacer",
        "indicacion_argumentos" : ["Explorador Camperor", "Explorador Brujular", "Explorador Hojar", "Usar carta skill"]
    },
    "lose_bullet" : {
        "tipo" : "automatico", # Caso especial que no se puede elegir si no se tiene
        "comando" : "command_losebullet"
    },
    "lose_life" : {
        "tipo" : "indicaciones",
        "comando" : "command_lose_life",
        "indicacion" : "Elija a un explorador para perder una vida",
        "indicacion_argumentos" : ["Explorador Campero", "Explorador Brujula", "Explorador Hoja"]
    },
    "lose_food" : {
        "tipo" : "automatico",
        "comando" : "command_losefood"
    },
    "lose_explorer" : {
        "tipo" : "indicaciones",
        "comando" : "command_lose_explorer",
        "indicacion" : "Elija a un explorador para morir",
        "indicacion_argumentos" : ["Explorador Campero", "Explorador Brujula", "Explorador Hoja"]
    },
}

opciones_opcional = {
    1 : {
        "comandos" : {
            1 : "Realizar acción opcional"
        }
    },
    2 : {
        "comandos" : {
            1 : "No hacer acción opcional"
        }
    }
}

cartas_aventura = {
    0.5 : {
        "nombre" : "¡Nido Enorme!",
        "plastilla" : "1",
        "fila" : "0",
        "columna" : "0",
        "acciones" : {
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
                            1 : "remove_rute",
                            2 : "remove_rute",
                            3 : "remove_rute",                            
                        }
                    }
                }            
            }
        }
    },
    1 : {
        "nombre" : "¡Campamento Abandonado!",
        "plastilla" : "1",
        "fila" : "0",
        "columna" : "1",
        "acciones" : {
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
        "nombre" : "Xinguano",
        "plastilla" : "1",
        "fila" : "0",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_skill",
                            3 : "swap_rute",
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life",
                            3 : "gain_progreso"                           
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_explorer"                     
                        }
                    }
                }
            }
        }
    },
    3 : {
        "nombre" : "Kalapalos",
        "plastilla" : "1",
        "fila" : "1",
        "columna" : "0",
        "acciones" : {
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
        "nombre" : "Claro",
        "plastilla" : "1",
        "fila" : "1",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "opcional", # si es de tipo opcional se puede obviar de hacerla
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp",
                            2 : "gain_food",
                            3 : "gain_food"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional", # si es de tipo opcional se puede obviar de hacerla
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp",
                            2 : "gain_life",
                        }
                    }
                }
            }
        }
    },
    5 : {
        "nombre" : "El camino por delante",
        "plastilla" : "1",
        "fila" : "1",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "add_rute"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional", # si es de tipo opcional se puede obviar de hacerla
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "gain_progreso",
                        }
                    }
                }
            },
            3 : {
                "tipo" : "opcional", # si es de tipo opcional se puede obviar de hacerla
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_food",
                        }
                    }
                }
            }
        }
    },
    6 : {
        "nombre" : "Jaguar",
        "plastilla" : "1",
        "fila" : "2",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life",
                            3 : "remove_rute"                            
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_skill"                        
                        }
                    }
                }
            }
        }
    },
    7 : {
        "nombre" : "Niebla Espesa",
        "plastilla" : "1",
        "fila" : "2",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "swap_rute",
                            3 : "remove_rute"                            
                        }
                    }
                }
            }
        }
    },
    8 : {
        "nombre" : "¡Huellas!",
        "plastilla" : "1",
        "fila" : "2",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "remove_rute",
                            2 : "gain_progreso"                        
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "gain_food",
                            2 : "gain_food",
                            2 : "gain_food"
                        }
                    }
                }
            }
        }
    },
    9 : {
        "nombre" : "Murcielagos Vampiro",
        "plastilla" : "2",
        "fila" : "0",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food"                        
                        }
                    }
                }
            },
            2 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp"   
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life"
                        }
                    }
                }
            }
        }        
    },
    10 : {
        "nombre" : "Hierbas Curativas",
        "plastilla" : "2",
        "fila" : "0",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "remove_rute"                        
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_leaf",
                            2 : "gain_life",
                            3 : "gain_life",
                            4 : "add_rute",
                        }
                    }
                }
            }
        } 
    },
    10.5 : {
        "nombre" : "¡Ataque de dinosaurios!",
        "plastilla" : "2",
        "fila" : "0",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life",
                            3 : "swap_rute",
                            4 : "remove_rute",
                            5 : "remove_rute",
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "lose_bullet",
                            3 : "gain_food",
                            4 : "gain_food",
                            5 : "gain_skill",
                        }
                    }
                }
            }
        }
    },
    11 : {
        "nombre" : "Sendero Viejo",
        "plastilla" : "2",
        "fila" : "1",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "gain_progreso",
                            2 : "add_rute"                           
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "gain_skill"                     
                        }
                    }
                }
            }
        }
    },
    12 : {
        "nombre" : "Anaconda",
        "plastilla" : "2",
        "fila" : "1",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_food"                           
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_skill"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life"
                        }
                    }
                }
            }
        }
    },
    13 : {
        "nombre" : "Bakairi",
        "plastilla" : "2",
        "fila" : "1",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "gain_skill"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "swap_rute"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life"
                        }
                    }
                }
            }
        }
    },
    14 : {
        "nombre" : "Amanaye",
        "plastilla" : "2",
        "fila" : "2",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "gain_skill"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "lose_food",
                            3 : "gain_progreso"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "remove_rute",
                            3 : "remove_rute"
                        }
                    },
                    4 : {
                        "comandos" : {
                            1 : "lose_explorer"
                        }
                    }
                }
            }
        }
    },
    15 : {
        "nombre" : "Pirañas",
        "plastilla" : "2",
        "fila" : "2",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "lose_food",
                            3 : "gain_progreso"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "gain_progreso",
                            2 : "lose_life"
                        }
                    }
                }
            }
        }
    },
    16 : {
        "nombre" : "Rana Venenosa",
        "plastilla" : "2",
        "fila" : "2",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "remove_rute"
                        }
                    }
                }
            },
            1 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "gain_skill"
                        }
                    }
                }
            }
        }
    },
    17 : {
        "nombre" : "Emboscada",
        "plastilla" : "3",
        "fila" : "0",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            1 : "remove_rute",
                            1 : "add_rute"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life"   
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_leaf",
                            2 : "lose_leaf"
                        }
                    }
                }
            }
        }  
    },
    18 : {
        "nombre" : "Progreso",
        "plastilla" : "3",
        "fila" : "0", 
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "gain_progreso"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "gain_food",
                            3 : "gain_food"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_leaf",
                            2 : "gain_food",
                            3 : "gain_food"
                        }
                    },
                    4 : {
                        "comandos" : {
                            1 : "gain_life"
                        }
                    }
                }
            }
        }
    },
    19 : {
        "nombre" : "Camino Empinado",
        "plastilla" : "3",
        "fila" : "0",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life",
                            3 : "remove_rute",
                            4 : "gain_progreso"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "gain_skill"
                        }
                    }
                }
            }
        }
    },
    20 : {
        "nombre" : "Cascabel Muda",
        "plastilla" : "3",
        "fila" : "1", 
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_food"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life"
                        }
                    }
                }
            }
        }
    },
    20.5 : {
        "nombre" : "¡Poseido!",
        "plastilla" : "3",
        "fila" : "1", 
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_explorer",
                            2 : "gain_life",
                            3 : "gain_life",
                            4 : "gain_food",
                            5 : "gain_food",
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_explorer",
                            2 : "gain_life",
                            3 : "gain_food",
                            4 : "gain_bullet",
                            5 : "gain_bullet",
                            6 : "gain_bullet",
                        }
                    }
                }
            }
        }
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

opciones_choose_posible_role = {
    "Liberal" : {
        "comandos" : {
            1 : "Liberal"
        }
    },
    "Fascista" : {
        "comandos" : {
            1 : "Fascista"
        }
    },
    "Fascista" : {        
        "comandos" : {
            1 : "Hitler"
        }
    },
    "Fascista o Hitler" : {        
        "comandos" : {
            1 : "Fascista o Hitler"
        }
    }
}
