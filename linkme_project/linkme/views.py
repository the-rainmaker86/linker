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
        first_name = request.POST.get("first")
        second_name = request.POST.get("second")
        # For this example, assume both inputs are actor names.
        try:
            first_actor = Actor.objects.get(name=first_name)
            second_actor = Actor.objects.get(name=second_name)
        except Actor.DoesNotExist:
            context["error"] = "One or both actors not found."
            return render(request, "linkme/linkme.html", context)
        
        # Build the graph
        graph = build_graph()
        start = f"actor:{first_actor.id}"
        goal = f"actor:{second_actor.id}"
        path = find_connection(graph, start, goal)
        if path:
            # Build a list of objects based on the keys
            true_path = []
            for step in path:
                if step.startswith("actor:"):
                    actor_id = int(step.split(":")[-1])
                    true_path.append(Actor.objects.get(id=actor_id))
                elif step.startswith("movie:"):
                    movie_id = int(step.split(":")[-1])
                    true_path.append(Movie.objects.get(id=movie_id))
            context["true_path"] = true_path
        else:
            context["error"] = "No connection found."
    
    return render(request, "linkme/linkme.html", context)
