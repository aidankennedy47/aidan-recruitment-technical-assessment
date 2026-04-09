from flask import Flask, request
from typing import List, Dict, Union

# ==== DO NOT CHANGE ==========================================================
app = Flask(__name__)

# ==== Type Definitions, feel free to add or modify ===========================
project_registry: Dict[str, Dict] = {}

class Slug:
    def __init__(self, slug: str):
        self.slug = slug


class ProjectEntry:
    def __init__(self, name: str, requiredResources: List[Dict[str, Union[str, int]]]):
        self.type = "project"
        self.name = name
        self.requiredResources = requiredResources


class ResourceEntry:
    def __init__(self, name: str, buildTime: int):
        self.type = "resource"
        self.name = name
        self.buildTime = buildTime

# ==== Task 1 =================================================================
@app.route("/slugToTitle", methods=["GET"])
def slug_to_title():
    slug = request.args.get("slug")
    # TODO: Convert hyphenated lowercase string into title-cased string
    return "", 200

# ==== Task 2 =================================================================
@app.route("/projectEntry", methods=["POST"])
def add_project_entry():
    data = request.get_json()
    # TODO: Validate input and store in `project_registry`
    if not data or "type" not in data or "name" not in data:
        return "", 400
    
    #type is not project or resource
    if data["type"] not in ["project", "resource"]:
        return "", 400
    
    #name is not unique
    if data["name"] in project_registry:
        print("Duplicate project exists!")
        return "", 400
    
    #check for projects
    if data["type"] == "project":
        if "requiredResources" not in data:
            return "", 400
        
        seen = set()

        for r in data["requiredResources"]:
            if r["name"] not in seen:
                seen.add(r["name"])
                continue
            print("Duplicate resource found!")
            return "", 400

    #check for resources
    elif data["type"] == "resource":
        if "buildTime" not in data:
            print("Buildtime not in data!")
            return "", 400
        
        #0 buildtime for resource
        if data["buildTime"] < 0:
            print("Buildtime less than 0!!")
            return "", 400
    
    print(data)
    project_registry[data["name"]] = data
    print(project_registry)
    return "", 200


# ==== Task 3 =================================================================
@app.route("/summary", methods=["GET"])
def get_summary():
    name = request.args.get("name")
    # TODO: Lookup entry and compute total build time and base resources
    
    #validate input (check if exists)
    if not name or name not in project_registry:
        return "", 400

    #lookup valid project
    entry = project_registry[name]

    #check if project, not a resource
    if entry["type"] != "project":
        return "", 400

    #way to keep track of resources
    resourceCounts = {}

    #recursively look up values for the entry if it is a project and add the buildtime, else if it is a resource, add the buildtime and end
    #for projects only
    def recurse(currentName, multiplier):
        if currentName not in project_registry:
            return -1
        
        current = project_registry[currentName]

        #what is the base case? resource
        if current["type"] == "resource":
            currBuildTime = current["buildTime"]

            if currentName not in resourceCounts:
                resourceCounts[currentName] = 0
            resourceCounts[currentName] += multiplier

            return currBuildTime * multiplier

        #transition case = project
        total = 0

        for dependency in current["requiredResources"]:
            dependencyName = dependency["name"]
            quantity = dependency["quantity"]

            result = recurse(dependencyName, multiplier * quantity)

            if result == -1:
                return -1
            
            total += result
        
        return total

    totalTime = recurse(name, 1)

    if totalTime == -1:
        return "", 400

    #formatting answer
    resourcesList = []
    for rName, qty in resourceCounts.items():
        resourcesList.append({"name":rName, "quantity":qty})
    
    #returns full list of underlying base resources and total build time
    return {"name":name, "buildTime":totalTime, "resources":resourcesList}, 200


# ==== DO NOT CHANGE ==========================================================
if __name__ == "__main__":
    app.run(debug=True, port=8080)
