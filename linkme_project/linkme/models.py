# movies/models.py
from collections import deque
from django.db import models
import re 
import requests



TMDB_API_KEY = '1a091ae4d3dab25fd731c8f5025920af'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'


def get_movie_poster(movie_title):
    # Query TMDb search endpoint using the movie title.
    params = {
        'api_key': TMDB_API_KEY,
        'query': movie_title
    }
    response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
    if response.status_code == 200:
        data = response.json()
        print('data is', data)
        if data['results']:
            # Use the first result's poster_path.
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None



def seed(num):
    links = Link.objects.all()[:num]
    for link in links:
        actor, actor_created = Actor.objects.get_or_create(name=link.actor)
        movie, movie_created = Movie.objects.get_or_create(title=link.movie)
        # print(f"Seeded: Actor: {actor.name} (Created: {actor_created}), Movie: {movie.title} (Created: {movie_created})")
        
class Link(models.Model):
    actor = models.TextField(db_column='Actor', blank=True, null=True)  # Field name made lowercase.
    movie = models.TextField(db_column='Movie', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'linkme'

def find_connection(graph, start, goal):
    # BFS to find the shortest path from start to goal.
    queue = deque([[start]])
    visited = set()

    while queue:
        path = queue.popleft()
        node = path[-1]
        # print('path is', path)
        # print('node is', node)
        # print(node)
        if node == goal:
            return path
        if node in visited:
            continue
        visited.add(node)
        # print('visited is', visited)
        for neighbor in graph.get(node, []): #for all the node's neighbors
            new_path = list(path)
            new_path.append(neighbor)
            queue.append(new_path)
    return None  # No connection found.

class Actor(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255, unique=True)
    release_year = models.IntegerField(null=True, blank=True)
    cast = models.ManyToManyField(Actor, related_name="movies")

    def __str__(self):
        return self.title
    
links = Link.objects.all()

def seed_casts(num):
    movies = Movie.objects.all()[:num]
    for movie in movies:
        # Query the Link table for all actor names associated with this movie title.
        actor_names = Link.objects.filter(movie=movie.title).values_list('actor', flat=True)
        for actor_name in actor_names:
            # Get or create an Actor instance by name.
            actor, created = Actor.objects.get_or_create(name=actor_name)
            movie.cast.add(actor)
        movie.save()
    
def build_graph():
    graph = {}
    # Get the through model for the ManyToManyField.
    through_model = Movie.cast.through
    # print('Movie.cast.through is', through_model)
    # Retrieve all relationships as (movie_id, actor_id) tuples.
    relations = through_model.objects.all().values_list('movie_id', 'actor_id')
    for movie_id, actor_id in relations:
        movie_key = f"movie:{movie_id}"
        actor_key = f"actor:{actor_id}"
        # print('movie_key is', movie_key)
        # print('actor key is', actor_key)
        # Add the relationship in both directions.
        # graph.setdefault(movie_key, []).append(actor_key)
        # graph.setdefault(actor_key, []).append(movie_key)
        try:
            graph[movie_key].append(actor_key)
        except KeyError:
            graph[movie_key] = []
        try:
            graph[actor_key].append(movie_key)
        except KeyError:
            graph[actor_key] = []
       
    # print(graph)
    return graph
