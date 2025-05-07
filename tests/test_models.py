from src.models.movie import Movie

def test_movie_model():
    
    movie = Movie(title="Titanic", year=1997)
    assert movie.title == "Titanic"