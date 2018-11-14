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
        "indicacion_argumentos" : ["Campero -1❤️", "Brujula -2❤️", "Hoja -2❤️", "Usar carta skill"]
    },
    "lose_leaf" : {
        "tipo" : "indicaciones",
        "comando" : "command_lose_leaf",
        "indicacion" : "Elija que quiere hacer",
        "indicacion_argumentos" : ["Campero -2❤️", "Brujula -2❤️", "Hoja -1❤️", "Usar carta skill"]
    },
    "lose_compass" : {
        "tipo" : "indicaciones",
        "comando" : "command_lose_compass",
        "indicacion" : "Elija que quiere hacer",
        "indicacion_argumentos" : ["Campero -2❤️", "Brujula -1❤️", "Hoja -2❤️", "Usar carta skill"]
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
        "nombre" : "Escorpión",
        "plastilla" : "3",
        "fila" : "1",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp",
                            2 : "add_rute",
                            3 : "swap_rute"
                        }
                    }
                }
            }
        }        
    },
    22 : {
        "nombre" : "Xavante",
        "plastilla" : "3",
        "fila" : "2",
        "columna" : "0",
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
                            1 : "lose_compass",
                            2 : "gain_progreso"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_explorer",
                            2 : "gain_progreso"
                        }
                    }
                }
            }
        }
    },
    23 : {
        "nombre" : "Enjambre",
        "plastilla" : "3",
        "fila" : "2", 
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_life"
                        }
                    }
                }
            }
        }
    },
    24 : {
        "nombre" : "Hormigas",
        "plastilla" : "3",
        "fila" : "2", 
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "remove_rute",
                            2 : "remove_rute"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
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
    25 : {
        "nombre" : "Cocodrilo",
        "plastilla" : "4",
        "fila" : "0",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_food",
                            3 : "gain_food"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "add_rute",
                            2 : "add_rute"
                        }
                    }
                }
            }
        }        
    },
    26 : {
        "nombre" : "Chaparron",
        "plastilla" : "4",
        "fila" : "0",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp",
                            2 : "lose_food",
                            3 : "swap_rute",
                            4 : "remove_rute"
                        }
                    }
                }
            }
        }   
    },
    27 : {
        "nombre" : "Araña Venenosa",
        "plastilla" : "4",
        "fila" : "0",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "swap_rute"
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
                            1 : "lose_explorer"
                        }
                    }
                }
            }
        } 
    },
    28 : {
        "nombre" : "Herida Infectada",
        "plastilla" : "4",
        "fila" : "1",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "gain_skill",
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
                            1 : "lose_compass"
                        }
                    }
                }
            }
        } 
    },
    29 : {
        "nombre" : "Rapidos",
        "plastilla" : "4",
        "fila" : "1",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "add_rute",
                            3 : "gain_progreso"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "lose_compass",
                            3 : "gain_progreso"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "swap_rute",
                            3 : "swap_rute"
                        }
                    }
                }
            }            
        }
    },
    30 : {
        "nombre" : "Puma",
        "plastilla" : "4",
        "fila" : "1",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_skill"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_leaf"
                        }
                    }
                }
            }           
        }
    },
    31 : {
        "nombre" : "Infección De Parasitos",
        "plastilla" : "4",
        "fila" : "2",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_life"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_bullet"
                        }
                    }
                }
            }
        }
    },
    32 : {
        "nombre" : "Ruinas",
        "plastilla" : "4",
        "fila" : "2",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "remove_last_rute",
                            3 : "remove_last_rute"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_compass",
                            3 : "gain_progreso"
                        }
                    }
                }
            },
            3 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "lose_camp",
                            3 : "gain_progreso"
                        }
                    }
                }
            }
        }
    },
    33 : {
        "nombre" : "¡Lesión'",
        "plastilla" : "4",
        "fila" : "2",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp",
                            2 : "lose_life",
                            3 : "lose_life"
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
                            2 : "gain_food",
                            3 : "gain_food"
                        }
                    }
                }
            }
        }
    },
    34 : {
        "nombre" : "Perdido",
        "plastilla" : "5",
        "fila" : "0",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "add_rute",
                            2 : "add_rute",
                            3 : "gain_skill",
                            4 : "remove_rute"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "lose_compass",
                            3 : "gain_progreso"
                        }
                    }
                }
            }
        }        
    },
    35 : {
        "nombre" : "Tormenta Electrica",
        "plastilla" : "5",
        "fila" : "0",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "remove_rute",
                            2 : "remove_rute",
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
                            1 : "lose_camp"
                        }
                    }
                }
            }
        } 
    },
    36 : {
        "nombre" : "Insectos",
        "plastilla" : "5",
        "fila" : "0",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "remove_rute",
                            3 : "gain_skill",
                            4 : "remove_last_rute"
                        }
                    }
                }
            }
        } 
    },
    37 : {
        "nombre" : "Anguilas Electricas",
        "plastilla" : "5",
        "fila" : "1",
        "columna" : "0",
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
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
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
    38 : {
        "nombre" : "Mochila Rota",
        "plastilla" : "5",
        "fila" : "1",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "swap_rute"
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
                            1 : "lose_life"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_bullet"
                        }
                    }
                }
            }
        } 
    },
    39 : {
        "nombre" : "Cruzar El Rio",
        "plastilla" : "5",
        "fila" : "1",
        "columna" : "2",
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
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "gain_skill"   
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "gain_progreso",
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "gain_progreso",
                            2 : "lose_life",
                        }
                    }
                }
            }
        }
    },
    40 : {
        "nombre" : "Pantera Negra",
        "plastilla" : "5",
        "fila" : "2",
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "gain_skill"
                        }
                    }
                }
            },
            2 : {
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
                            1 : "lose_food",
                            2 : "lose_food",
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life",
                        }
                    }
                }
            }
        }        
    },
    40.5 : {
        "nombre" : "¡Idolo De Oro!",
        "plastilla" : "5",
        "fila" : "2",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "gain_skill"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "lose_food",
                            3 : "gain_life",
                            4 : "gain_life"
                        }
                    }
                }
            }
        }
    },
    41 : {
        "nombre" : "Pecarí",
        "plastilla" : "5",
        "fila" : "2",
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "gain_skill",
                            2 : "remove_rute"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_leaf",
                            2 : "gain_food",
                            3 : "gain_food",
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "gain_food",
                            3 : "gain_food",
                        }
                    }
                }
            }
        }        
    },
    42 : {
        "nombre" : "Awa",
        "plastilla" : "6",
        "fila" : "0",
        "columna" : "0",
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
                            1 : "lose_food",
                            2 : "gain_life"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "gain_progreso"
                        }
                    }
                }
            }
        }                
    },
    43 : {
        "nombre" : "Fiebre",
        "plastilla" : "6",
        "fila" : "0",
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "swap_rute"
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
                            1 : "lose_camp"
                        }
                    }
                }
            }
        }
    },
    44 : {
        "nombre" : "HI'AITO'IHI",
        "plastilla" : "6",
        "fila" : "0", 
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "lose_life",
                            3 : "gain_progreso"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_explorer",
                            2 : "gain_progreso"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "gain_skill"
                        }
                    }
                }
            }
        } 
    },
    45 : {
        "nombre" : "Hierba Mora",
        "plastilla" : "6",
        "fila" : "1", 
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "swap_rute"
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
                            1 : "lose_leaf"
                        }
                    }
                }
            }
        }
    },
    46 : {
        "nombre" : "Refugio Abandonado",
        "plastilla" : "6",
        "fila" : "1", 
        "columna" : "1",
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
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "gain_bullet",
                            2 : "gain_bullet"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "gain_life",
                            2 : "gain_skill"
                        }
                    }
                }
            }
        }
    },
    47 : {
        "nombre" : "Árbol Kapok",
        "plastilla" : "6",
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
                    }
                }
            },
            2 : {
                "tipo" : "opcional",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "gain_life",
                            3 : "remove_last_rute"
                        }
                    }
                }
            }
        }
    },
    48 : {
        "nombre" : "Posición Ventajosa",
        "plastilla" : "6",
        "fila" : "2", 
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "swap_rute",
                            3 : "gain_skill"
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
                            2 : "gain_food"
                        }
                    }
                }
            }
        }
    },
    49 : {
        "nombre" : "Tapirape",
        "plastilla" : "6",
        "fila" : "2", 
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_leaf",
                            2 : "gain_progreso"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "gain_skill"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_leaf",
                            2 : "gain_life"
                        }
                    }
                }
            }
        }
    },
    50 : {
        "nombre" : "Puente De Cuerda",
        "plastilla" : "6",
        "fila" : "2", 
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "swap_rute"
                        }
                    }
                }
            },
            2 : {
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
                            1 : "gain_progreso",
                            2 : "lose_explorer"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "add_rute"
                        }
                    }
                }
            }
        } 
    },
    50.5 : {
        "nombre" : "¡Chicas Listas!",
        "plastilla" : "7",
        "fila" : "0", 
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "gain_skill"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_bullet",
                            2 : "lose_bullet"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "lose_explorer",
                            2 : "lose_life"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_compass",
                            2 : "lose_camp",
                            3 : "lose_bullet"
                        }
                    }
                }
            }
        } 
    },
    51 : {
        "nombre" : "Mono",
        "plastilla" : "7",
        "fila" : "0", 
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_food",
                            2 : "gain_skill"
                        }
                    }
                }
            }
        }
    },
    52 : {
        "nombre" : "Deplome De Terraplén",
        "plastilla" : "7",
        "fila" : "0", 
        "columna" : "2",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_food",
                            3 : "swap_rute"
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
                            1 : "lose_camp"
                        }
                    }
                }
            }
        } 
    },
    53 : {
        "nombre" : "Sanguijuelas",
        "plastilla" : "7",
        "fila" : "1", 
        "columna" : "0",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_food",
                            3 : "remove_last_rute"
                        }
                    }
                }
            }
        }
    },
    54 : {
        "nombre" : "Deshidratación",
        "plastilla" : "7",
        "fila" : "1", 
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_camp",
                            2 : "lose_camp"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "add_rute",
                            2 : "add_rute"
                        }
                    }
                }
            }
        } 
    },
    55 : {
        "nombre" : "Suministros Estropeados",
        "plastilla" : "7",
        "fila" : "1", 
        "columna" : "2",
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
            }
        } 
    },
    56 : {
        "nombre" : "Pantano",
        "plastilla" : "7",
        "fila" : "2", 
        "columna" : "0",
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
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_compass"
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
    99.5 : {
        "nombre" : "¡Trampa Antigua!",
        "plastilla" : "7",
        "fila" : "2", 
        "columna" : "1",
        "acciones" : {
            1 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "add_rute",
                            2 : "add_rute",
                            3 : "swap_rute"
                        }
                    }
                }
            },
            2 : {
                "tipo" : "obligatoria",
                "opciones" : {
                    1 : {
                        "comandos" : {
                            1 : "lose_explorer",
                            2 : "gain_progreso",
                            3 : "gain_progreso",
                            4 : "gain_progreso"
                        }
                    },
                    2 : {
                        "comandos" : {
                            1 : "gain_progreso"
                        }
                    },
                    3 : {
                        "comandos" : {
                            1 : "lose_life",
                            2 : "lose_life",
                            3 : "gain_progreso",
                            4 : "gain_progreso"
                        }
                    }
                }
            }
        }        
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
