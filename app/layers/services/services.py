# capa de servicio/lógica de negocio

from ..transport import transport
from ...config import config
from ..persistence import repositories
from ..utilities import translator
from django.contrib.auth import get_user

# función que devuelve un listado de cards. Cada card representa una imagen de la API de Pokemon
def getAllImages():
    # debe ejecutar los siguientes pasos:
    lista_imagenes_crudas=transport.getAllImages()  # 1) traer un listado de imágenes crudas desde la API (ver transport.py)
    lista_cards=[]
    for dato in lista_imagenes_crudas:    # 2) convertir cada img. en una card.
        card=translator.fromRequestIntoCard(dato)
        tipos=[]
        tipos_cartas= card.types
        for tipo in tipos_cartas:
            tipos.append(get_type_icon_url_by_name(tipo))
        card.types_imgs=tipos
        lista_cards.append(card)# 3) añadirlas a un nuevo listado que, finalmente, se retornará con todas las card encontradas.
    return lista_cards

# función que filtra según el nombre del pokemon.
def filterByCharacter(name):
    filtered_cards = []
    name=name.lower()
    for card in getAllImages():
        if name in card.name:  # debe verificar si el name está contenido en el nombre de la card, antes de agregarlo al listado de filtered_cards.
            filtered_cards.append(card)

    return filtered_cards

# función que filtra las cards según su tipo.
def filterByType(type_filter):
    filtered_cards = []
    lista_imagenes=getAllImages()
    type_filter=type_filter.lower()
    for card in lista_imagenes:
        if type_filter in card.types:# debe verificar si la casa de la card coincide con la recibida por parámetro. Si es así, se añade al listado de filtered_cards.
            filtered_cards.append(card)

    return filtered_cards

# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    fav = '' # transformamos un request en una Card (ver translator.py)
    fav.user = get_user(request) # le asignamos el usuario correspondiente.

    return repositories.save_favourite(fav) # lo guardamos en la BD.

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    if not request.user.is_authenticated:
        return []
    else:
        user = get_user(request)

        favourite_list = [] # buscamos desde el repositories.py TODOS Los favoritos del usuario (variable 'user').
        mapped_favourites = []

        for favourite in favourite_list:
            card = '' # convertimos cada favorito en una Card, y lo almacenamos en el listado de mapped_favourites que luego se retorna.
            mapped_favourites.append(card)

        return mapped_favourites

def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.delete_favourite(favId) # borramos un favorito por su ID

#obtenemos de TYPE_ID_MAP el id correspondiente a un tipo segun su nombre
def get_type_icon_url_by_name(type_name):
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        return None
    return transport.get_type_icon_url_by_id(type_id)