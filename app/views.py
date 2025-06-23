# capa de vista/presentación

from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login#importacion de funciones y clases necesarias para autenticación de usuarios y envío de correos electrónicos
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Favourite
import ast

def register_view(request):
    mensaje = ''
    if request.method == 'POST':
        nombre = request.POST.get('first_name', '').strip()
        apellido = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Validar que no exista usuario con ese username
        if User.objects.filter(username=username).exists():
            mensaje = 'El nombre de usuario ya existe. Por favor elija otro.'
        else:
            # Crear usuario
            user = User.objects.create_user(username=username, password=password,
                                            email=email, first_name=nombre, last_name=apellido)
            user.save()

            # Enviar mail con credenciales
            asunto = 'Registro exitoso'
            cuerpo = f'Hola {nombre},\n\nTu registro fue exitoso.\nTus credenciales son:\nUsuario: {username}\nContraseña: {password}\n\nGracias por registrarte.'
            send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, [email])

            return redirect('login')  # o donde quieras redirigir tras registro exitoso

    return render(request, 'register.html', {'mensaje': mensaje})

def login_view(request):
    mensaje = ''
    if request.method == 'POST':#Verifica si el usuario envió el formulario
        username = request.POST.get('username')#Extrae los datos del formulario
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)#verifica si los datos son correctos.
        if user is not None:#Si el usuario existe, se hace login
            login(request, user)
            return redirect('index-page')
    return render(request, 'login.html', {'mensaje': mensaje})

def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados: uno de las imágenes de la API y otro de favoritos, ambos en formato Card, y los dibuja en el template 'home.html'.
def home(request):
    lista_cards=services.getAllImages()
    images = []
    favourite_list = []
    if request.user.is_authenticated:
        favourite_list = [fav.id for fav in Favourite.objects.filter(user=request.user)]
    for card in lista_cards:
        images.append(card)
    return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })

# función utilizada en el buscador.
def search(request):
    name = request.POST.get('query', '')

    # si el usuario ingresó algo en el buscador, se deben filtrar las imágenes por dicho ingreso.
    if name != '':
        images = services.filterByCharacter(name)
        favourite_list = []

        return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })
    else:
        return redirect('home')

# función utilizada para filtrar por el tipo del Pokemon
def filter_by_type(request):
    type = request.POST.get('type', '')

    if type != '':
        images = services.filterByType(type) # debe traer un listado filtrado de imágenes, segun si es o contiene ese tipo.
        favourite_list = []

        return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })
    else:
        return redirect('home')

# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    favs = Favourite.objects.filter(user=request.user)
    return render(request, 'favourites.html', {'favourite_list': favs})

@login_required
def saveFavourite(request):
    if request.method == 'POST':
        user = request.user
        poke_id = request.POST.get('id')
        name = request.POST.get('name')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        types = request.POST.get('types')  # viene como string
        image = request.POST.get('image')
        # Convertir el string de tipos en lista (si viene como string tipo Python)
        try:
            types_list = ast.literal_eval(types)
        except:
            types_list = [types]  # fallback por si viene como solo un string

        try:
            Favourite.objects.create(
                poke_id=poke_id,
                name=name,
                height=height,
                weight=weight,
                types=types_list,
                image=image,
                user=user
            )
        except:
            pass  # evitar duplicados

    return redirect('home')

@login_required
def deleteFavourite(request):
    if request.method == 'POST':
        poke_id = request.POST.get('id')
        Favourite.objects.filter(user=request.user, id=poke_id).delete()
    return redirect('favoritos')

@login_required
def exit(request):
    logout(request)
    return redirect('home')