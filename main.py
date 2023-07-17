import datetime
from fastapi import Depends, HTTPException, Request,FastAPI,Body, Path, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from jwt_manager import create_token, validate_token   
from pydantic import BaseModel,Field
from typing import Optional, List
app = FastAPI()

#Para cambiar el nombre de la aplicacion
app.title = "Mi app con FastAPI"

#Para cambiar la version de la aplicacion
app.version = "0.0.1"

class JWTBearer(HTTPBearer):
  async def __call__(self, request:Request):
    auth = await super().__call__(request)
    data = validate_token(auth.credentials)
    if data['email'] != "admin@gmail.com":
        raise HTTPExcepction(status_code=403, detail="Credenciales son validas")

class User(BaseModel):
    email:str
    password:str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=datetime.date.today().year) #le:less than or equal
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=5, max_length=15)

    model_config = {
        "json_schema_extra": {
                "examples": [
                    {
                        "id": 1,
                        "title": "Mi Pelicula",
                        "overview": "Descripcion de la pelicula",
                        "year": 2022,
                        "rating": 9.9,
                        "category": "Acción"
                    }
                ]
            }
        }
movies = [
    {
        'id': 1,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2009',
        'rating': 7.8,
        'category': 'Acción'    
    } ,

     {
        'id': 2,
        'title': 'Avatar 2',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2022',
        'rating': 7.8,
        'category': 'Acción'    
    } 
]

#los tags nos permite agrupar las rutas de la aplicacion

@app.get('/', tags=['home']) #Retornar HTML
def message():
    return HTMLResponse('<h1>Hello world </h1>')

@app.post('/login',tags=['auth'])
def login(user:User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
    return JSONResponse(status_code=200, content=token)


@app.get('/movies',tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200,content=movies)

    #JSONResponse devuelve los datos en formato JSON, FastApi por defecto
    #lo hace, por lo tanto no es necesario usarlo si no es en un caso
    #especifico

@app.get('/movie1s/{id}',tags=['movies'],response_model=Movie)
def get_movie(id: int = Path(ge=1, le=2000))-> Movie:
    for item in movies:
        if item["id"] == id:
            return JSONResponse(content=item)
    return JSONResponse(status_code = 404,content={"message":"No se encontró una pelicula con el id dado"})

@app.get('/movies2/{id}',tags=['movies'],response_model=Movie)#Parametros de ruta
def get_movieId(id: int = Path(ge=1, le=2000)):
   movie = list(movie for movie in movies if movie["id"] == id)
   return movie or "No se encontró una pelicula con el id dado"


@app.get('/moviesCategory_year/',tags=['movies'],response_model=List[Movie] or dict) #Query paramaters
def get_movies_by_category_year(category: str = Query(min_length=5, max_length=15), year: str = Query(le=datetime.date.today().year)) -> List[Movie] or dict:
   movie = list(movie for movie in movies if ((movie["category"] == category) and (movie["year"] == year)))
   if movie:
    return movie
   else:
     return JSONResponse(content={"message":"No se encontró una pelicula con los parametros dados"})

@app.get('/moviesCategory/',tags=['movies'],response_model=List[Movie]) #Query paramaters
def get_movies_by_category(category: str = Query(min_length=5, max_length=15))-> List[Movie] or dict:
   movie = list(movie for movie in movies if (movie["category"] == category))
   if movie:
    return movie
   else:
     return JSONResponse(content={"message":"No se encontró una pelicula con los parametros dados"})

@app.get('/moviesYear/',tags=['movies'],response_model=List[Movie]) #Query paramaters
def get_movies_by_year(year: str = Query(le=datetime.date.today().year)) -> List[Movie] or dict:
   movie = list(movie for movie in movies if (movie["year"] == year))
   if movie:
    return movie
   else:
     return JSONResponse(content={"message":"No se encontró una pelicula con los parametros dados"})

@app.post('/movies',tags=['movies'],response_model=dict,status_code=201) #Post crear
def create_movie(movie: Movie) -> dict:
    movies.append(movie.dict())
    return JSONResponse(status_code=201,content={"message":"Se he registrado la pelicula correctamente"})

@app.put('/movies/{id}',tags=['movies'],response_model=dict,status_code=200) #Put update
def update_movie(id:int, movie: Movie)->dict:
    movie = get_movie(id)
    movie = movie.dict()#Uso de la funcion get_movie
    if type(movie) is not str:
        movie['title'] = movie.title
        movie['overview'] = movie.overview
        movie['year'] = movie.year
        movie['rating'] = movie.rating
        movie['category'] = movie.category
    else:
        return movie #Retorna mensaje de error
    return JSONResponse(status_code=200,content={"message":"Se he modificado la pelicula correctamente"})

@app.delete('/movies/{id}',tags=['movies'],response_model=dict,status_code=200) #Put update
def delete_movie(id:int)->dict:
    movie = get_movie(id)
    if movie:
        movies.remove(movie)
    return JSONResponse(status_code=200,content={"message":"Se he eliminado la pelicula correctamente"})