from django.shortcuts import render, HttpResponse
from linkme.models import *

# LINKS = Link.objects.all()
# ACTORS = Actor.objects.all()
# MOVIES = Movie.objects.all()

def home(request):
    return render(request, "linkme/linkme.html")

def connection_view(request):
    context = {}
    if request.method == "POST":
        # Retrieve input from the form
        first_input = request.POST.get("first")
        second_input = request.POST.get("second")
        is_actor_str = request.POST.get("is_actor", "true")
        is_actor = is_actor_str.lower() in ['true', '1', 'yes']
        
        try:
            if is_actor:
                first_item = Actor.objects.get(name=first_input)
                second_item = Actor.objects.get(name=second_input)
                start = f"actor:{first_item.id}"
                goal = f"actor:{second_item.id}"
            else:
                first_item = Movie.objects.filter(title__istartswith=first_input).first()
                second_item = Movie.objects.filter(title__istartswith=second_input).first()
                if not (first_item and second_item):
                    raise Movie.DoesNotExist
                start = f"movie:{first_item.id}"
                goal = f"movie:{second_item.id}"
        except (Actor.DoesNotExist, Movie.DoesNotExist):
            context["error"] = "One or both items not found."
            return render(request, "linkme/linkme.html", context)
        
        graph = build_graph()
        path = find_connection(graph, start, goal)
        if path:
            true_path = []
            for step in path:
                if step.startswith("actor:"):
                    actor_id = int(step.split(':')[-1])
                    actor = Actor.objects.get(id=actor_id)
                    true_path.append({"obj": actor, "type": "actor"})
                elif step.startswith("movie:"):
                    movie_id = int(step.split(':')[-1])
                    movie = Movie.objects.get(id=movie_id)
                    poster = get_movie_poster(movie.title)
                    true_path.append({"obj": movie, "type": "movie", "poster": poster})
                    print('poster url', true_path[-1]['poster'])
                    print('step.title is', step.title)
            context["true_path"] = true_path
            print("true path is", context['true_path'])
            # print('poster url is', context['poster'])
        else:
            context["error"] = "No connection found."
    
    return render(request, "linkme/linkme.html", context)
