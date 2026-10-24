# -*- coding: utf-8 -*-
from typing import List, Dict, Set
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
from core.graph import Graph
import heapq
from collections import deque

class GraphStep(VisualizationStep):
    def __init__(self, graph: Graph, visited: Set[int] = None, 
                 frontier: List[int] = None, current: int = None,
                 path: List[int] = None, distances: Dict[int, float] = None,
                 code_line=0, explanation="", comparisons=0, extra=None):
        e_dict = extra.copy() if extra else {}
        if graph is not None and "graph" not in e_dict:
            e_dict["graph"] = graph
        if visited is not None:
            e_dict["visited"] = visited
        elif "visited" not in e_dict:
            e_dict["visited"] = set()
        if frontier is not None:
            e_dict["frontier"] = frontier
        elif "frontier" not in e_dict:
            e_dict["frontier"] = []
        if current is not None and "current" not in e_dict:
            e_dict["current"] = current
        if path is not None:
            e_dict["path"] = path
        elif "path" not in e_dict:
            e_dict["path"] = []
        if distances is not None:
            e_dict["distances"] = distances
        elif "distances" not in e_dict:
            e_dict["distances"] = {}

        nodes_keys = list(graph.nodes.keys()) if hasattr(graph, "nodes") and isinstance(graph.nodes, dict) else []
        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            array=nodes_keys,
            highlight=[current] if current is not None else [],
            extra=e_dict
        )

class BFSPlugin(AlgorithmPluginBase):
    id = "bfs"
    name = "BFS - Szélességi keresés"
    description = "Szintenként bejár, legrövidebb út lépésszámban"
    time_complexity = "O(V+E)"
    space_complexity = "O(V)"
    icon = "🌊"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "graph"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("graph_size", "Gráf méret", "int", 5, 3, 8, description="Csomópontok / rács méret"))
        self.params.add(Param("density", "Sűrűség", "choice", "közepes", choices=["ritka", "közepes", "sűrű"], description="Élek sűrűsége"))
    
    def get_params(self):
        return self.params
    
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """def bfs(graf, start, cel):
    # Szélességi keresés - sor (queue)
    visited = set([start])
    queue = deque([start])
    parent = {start: None}
    while queue:
        u = queue.popleft()  # Sor eleje
        if u == cel:
            break
        for v, w in graf[u].neighbors:
            if v not in visited:
                visited.add(v)
                parent[v] = u
                queue.append(v)
    return parent""",
        "C++": """void BFS(Graph& g, int start) {
    queue<int> q;
    vector<bool> visited(g.V, false);
    visited[start]=true; q.push(start);
    while(!q.empty()){
        int u=q.front(); q.pop();
        for(auto [v,w]: g.adj[u]){
            if(!visited[v]){
                visited[v]=true;
                q.push(v);
            }
        }
    }
}""",
        "C": """void BFS(int graph[][V], int start){
    int visited[V]={0}, queue[V], front=0, rear=0;
    visited[start]=1; queue[rear++]=start;
    while(front<rear){
        int u=queue[front++];
        for(int v=0;v<V;v++){
            if(graph[u][v] && !visited[v]){
                visited[v]=1; queue[rear++]=v;
            }
        }
    }
}""",
        "BASIC": """SUB BFS(start)
    DIM visited(V): visited(start)=1
    DIM queue(V): qhead=0: qtail=0: queue(qtail)=start: qtail=1
    WHILE qhead<qtail
        u=queue(qhead): qhead=qhead+1
        FOR EACH v IN adj(u)
            IF visited(v)=0 THEN visited(v)=1: queue(qtail)=v: qtail=qtail+1
        NEXT
    WEND
END SUB""",
        "Java": """void BFS(Graph g, int start){
    Queue<Integer> q=new LinkedList<>();
    boolean[] visited=new boolean[g.V];
    visited[start]=true; q.add(start);
    while(!q.isEmpty()){
        int u=q.poll();
        for(int v: g.adj[u]){
            if(!visited[v]){visited[v]=true; q.add(v);}
        }
    }
}""",
        "Pascal": """procedure BFS(start: Integer);
var q: array of Integer; visited: array of Boolean; u,v: Integer;
begin
  visited[start]:=True; Enqueue(q,start);
  while not QueueEmpty(q) do begin
    u:=Dequeue(q);
    for v in adj[u] do
      if not visited[v] then begin visited[v]:=True; Enqueue(q,v); end;
  end;
end;"""
    }
    
    def get_steps(self, arr):
        g = Graph.create_sample_maze(5)
        if not g.nodes:
            g = Graph.create_random_weighted(6)
        start = min(g.nodes.keys()) if g.nodes else 0
        target = max(g.nodes.keys()) if g.nodes else 0
        
        visited = set([start])
        queue = deque([start])
        parent = {start: None}
        comparisons = 0
        
        yield GraphStep(g, visited=set([start]), frontier=[start], current=start, code_line=3,
                        explanation=f"🌊 BFS kezdés: start={start}, cél={target}, sor=[{start}]",
                        comparisons=0, extra={"start": start, "target": target, "queue": [start]})
        
        while queue:
            u = queue.popleft()
            comparisons+=1
            yield GraphStep(g, visited=visited, frontier=list(queue), current=u, code_line=6,
                            explanation=f"Kivesz sorból: u={u}, visited={len(visited)}",
                            comparisons=comparisons, extra={"start": start, "target": target, "queue": list(queue), "current": u})
            
            if u == target:
                # Út visszafejtés
                path = []
                cur = target
                while cur is not None:
                    path.append(cur)
                    cur = parent.get(cur)
                path.reverse()
                yield GraphStep(g, visited=visited, frontier=[], current=u, path=path, code_line=8,
                                explanation=f"✅ Cél elérve! Út: {' -> '.join(map(str, path))}",
                                comparisons=comparisons, extra={"start": start, "target": target, "path": path, "found": True})
                return
            
            for v, w in g.nodes[u].neighbors:
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)
                    yield GraphStep(g, visited=visited, frontier=list(queue), current=u, code_line=12,
                                    explanation=f"Felfedez: {u} -> {v} (súly {w}), sorba tesz",
                                    comparisons=comparisons, extra={"start": start, "target": target, "queue": list(queue), "edge": (u,v)})
        
        yield GraphStep(g, visited=visited, frontier=[], current=None, code_line=14,
                        explanation=f"❌ BFS vége, cél nem elérhető",
                        comparisons=comparisons, extra={"start": start, "target": target})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class DFSPlugin(AlgorithmPluginBase):
    id = "dfs"
    name = "DFS - Mélységi keresés"
    description = "Amíg lehet mélyre megy, verem (stack)"
    time_complexity = "O(V+E)"
    space_complexity = "O(V)"
    icon = "🕳️"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "graph"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("graph_size", "Gráf méret", "int", 5, 3, 8, description="Csomópontok / rács méret"))
        self.params.add(Param("density", "Sűrűség", "choice", "közepes", choices=["ritka", "közepes", "sűrű"], description="Élek sűrűsége"))
    
    def get_params(self):
        return self.params
    
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """def dfs(graf, start, cel):
    visited=set()
    stack=[start]
    parent={start: None}
    while stack:
        u=stack.pop()  # Verem teteje (LIFO)
        if u not in visited:
            visited.add(u)
            if u==cel: break
            for v,w in reversed(graf[u].neighbors):
                if v not in visited:
                    parent[v]=u
                    stack.append(v)
    return parent""",
        "C++": """void DFS(Graph& g, int start){
    stack<int> s; vector<bool> visited(g.V,false);
    s.push(start);
    while(!s.empty()){
        int u=s.top(); s.pop();
        if(!visited[u]){
            visited[u]=true;
            for(auto [v,w]: g.adj[u])
                if(!visited[v]) s.push(v);
        }
    }
}""",
        "C": "/* DFS C - verem */\nvoid DFS(int g[][V], int start){ int visited[V]={0}, stack[V], top=0; stack[top++]=start; while(top>0){int u=stack[--top]; if(!visited[u]){visited[u]=1; for(int v=0;v<V;v++) if(g[u][v] && !visited[v]) stack[top++]=v;}}}",
        "BASIC": "SUB DFS(start)\n DIM visited(V): DIM stack(V): top=0: stack(top)=start\n WHILE top>0\n  u=stack(top-1): top=top-1\n  IF visited(u)=0 THEN visited(u)=1: FOR EACH v IN adj(u): IF visited(v)=0 THEN stack(top)=v: top=top+1\n WEND\nEND SUB",
        "Java": "void DFS(Graph g, int start){ Stack<Integer> s=new Stack<>(); boolean[] visited=new boolean[g.V]; s.push(start); while(!s.isEmpty()){int u=s.pop(); if(!visited[u]){visited[u]=true; for(int v: g.adj[u]) if(!visited[v]) s.push(v);}}}",
        "Pascal": "procedure DFS(start: Integer); var s: array of Integer; visited: array of Boolean; u,v: Integer; begin Push(s,start); while not StackEmpty(s) do begin u:=Pop(s); if not visited[u] then begin visited[u]:=True; for v in adj[u] do if not visited[v] then Push(s,v); end; end; end;"
    }
    
    def get_steps(self, arr):
        g = Graph.create_sample_maze(5)
        start = min(g.nodes.keys()) if g.nodes else 0
        target = max(g.nodes.keys()) if g.nodes else 0
        visited = set()
        stack = [start]
        parent = {start: None}
        comparisons = 0
        
        yield GraphStep(g, visited=set(), frontier=[start], current=start, code_line=3,
                        explanation=f"🕳️ DFS kezdés: start={start}, cél={target}, verem=[{start}]",
                        comparisons=0, extra={"start": start, "target": target, "stack": [start]})
        
        while stack:
            u = stack.pop()
            comparisons+=1
            if u in visited:
                continue
            visited.add(u)
            yield GraphStep(g, visited=visited, frontier=list(stack), current=u, code_line=6,
                            explanation=f"Veremből kivesz: u={u}, mélyre megy",
                            comparisons=comparisons, extra={"start": start, "target": target, "stack": list(stack), "current": u})
            
            if u == target:
                path = []
                cur = target
                while cur is not None:
                    path.append(cur)
                    cur = parent.get(cur)
                path.reverse()
                yield GraphStep(g, visited=visited, frontier=[], current=u, path=path, code_line=8,
                                explanation=f"✅ Cél! Út: {' -> '.join(map(str, path))}",
                                comparisons=comparisons, extra={"start": start, "target": target, "path": path, "found": True})
                return
            
            for v, w in reversed(g.nodes[u].neighbors):
                if v not in visited:
                    parent[v] = u
                    stack.append(v)
                    yield GraphStep(g, visited=visited, frontier=list(stack), current=u, code_line=12,
                                    explanation=f"Felfedez mélyen: {u} -> {v}, verembe",
                                    comparisons=comparisons, extra={"start": start, "target": target, "stack": list(stack), "edge": (u,v)})
        
        yield GraphStep(g, visited=visited, frontier=[], current=None, code_line=14,
                        explanation="❌ DFS vége", comparisons=comparisons, extra={"start": start, "target": target})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class DijkstraPlugin(AlgorithmPluginBase):
    id = "dijkstra"
    name = "Dijkstra - Legrövidebb út"
    description = "Súlyozott gráfban legrövidebb út, mohó + prioritás sor"
    time_complexity = "O((V+E) log V)"
    space_complexity = "O(V)"
    icon = "🗺️"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "graph"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("graph_size", "Gráf méret", "int", 5, 3, 8, description="Csomópontok / rács méret"))
        self.params.add(Param("density", "Sűrűség", "choice", "közepes", choices=["ritka", "közepes", "sűrű"], description="Élek sűrűsége"))
    
    def get_params(self):
        return self.params
    
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """def dijkstra(graf, start):
    import heapq
    dist={node: float('inf') for node in graf}
    dist[start]=0
    pq=[(0,start)]
    parent={start: None}
    while pq:
        d,u=heapq.heappop(pq)
        if d>dist[u]: continue
        for v,w in graf[u].neighbors:
            if dist[u]+w < dist[v]:
                dist[v]=dist[u]+w
                parent[v]=u
                heapq.heappush(pq,(dist[v],v))
    return dist, parent""",
        "C++": """void Dijkstra(Graph& g, int start){
    vector<int> dist(g.V, INF); dist[start]=0;
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
    pq.push({0,start});
    while(!pq.empty()){
        auto [d,u]=pq.top(); pq.pop();
        if(d>dist[u]) continue;
        for(auto [v,w]: g.adj[u]){
            if(dist[u]+w < dist[v]){
                dist[v]=dist[u]+w; pq.push({dist[v],v});
            }
        }
    }
}""",
        "C": "/* Dijkstra C */\nvoid Dijkstra(int g[][V], int start){int dist[V], visited[V]={0}; for(int i=0;i<V;i++) dist[i]=INF; dist[start]=0; for(int c=0;c<V-1;c++){int u=minDist(dist,visited); visited[u]=1; for(int v=0;v<V;v++) if(!visited[v] && g[u][v] && dist[u]!=INF && dist[u]+g[u][v]<dist[v]) dist[v]=dist[u]+g[u][v];}}",
        "BASIC": "SUB Dijkstra(start)\n DIM dist(V): FOR i=0 TO V-1: dist(i)=INF: NEXT: dist(start)=0\n DIM visited(V)\n FOR c=0 TO V-2\n  u=MinDist(dist,visited): visited(u)=1\n  FOR EACH v,w IN adj(u): IF dist(u)+w < dist(v) THEN dist(v)=dist(u)+w\n NEXT\nEND SUB",
        "Java": "void Dijkstra(Graph g, int start){int[] dist=new int[g.V]; Arrays.fill(dist, INF); dist[start]=0; PriorityQueue<int[]> pq=new PriorityQueue<>(Comparator.comparingInt(a->a[0])); pq.add(new int[]{0,start}); while(!pq.isEmpty()){int[] cur=pq.poll(); int d=cur[0], u=cur[1]; if(d>dist[u]) continue; for(int[] e: g.adj[u]){int v=e[0], w=e[1]; if(dist[u]+w<dist[v]){dist[v]=dist[u]+w; pq.add(new int[]{dist[v],v});}}}}",
        "Pascal": "procedure Dijkstra(start: Integer); var dist: array of Integer; visited: array of Boolean; u,v,w: Integer; begin for i:=0 to V-1 do dist[i]:=INF; dist[start]:=0; for c:=0 to V-2 do begin u:=MinDist(dist,visited); visited[u]:=True; for v,w in adj[u] do if dist[u]+w<dist[v] then dist[v]:=dist[u]+w; end; end;"
    }
    
    def get_steps(self, arr):
        g = Graph.create_random_weighted(7)
        start = 0
        target = len(g.nodes)-1
        if target not in g.nodes: target = start
        
        dist = {node: float('inf') for node in g.nodes}
        dist[start] = 0
        pq = [(0, start)]
        parent = {start: None}
        visited = set()
        comparisons = 0
        
        yield GraphStep(g, visited=set(), frontier=[start], current=start, distances=dist, code_line=4,
                        explanation=f"🗺️ Dijkstra: start={start}, cél={target}, dist[{start}]=0",
                        comparisons=0, extra={"start": start, "target": target, "dist": dict(dist), "pq": [(0,start)]})
        
        while pq:
            d,u = heapq.heappop(pq)
            comparisons+=1
            if u in visited:
                continue
            if d > dist[u]:
                continue
            visited.add(u)
            yield GraphStep(g, visited=visited, frontier=[n for _,n in pq], current=u, distances=dist, code_line=8,
                            explanation=f"Kivesz pq-ból: u={u} dist={d}, visited",
                            comparisons=comparisons, extra={"start": start, "target": target, "dist": dict(dist), "pq": list(pq), "current": u})
            
            if u == target:
                path = []
                cur = target
                while cur is not None:
                    path.append(cur)
                    cur = parent.get(cur)
                path.reverse()
                yield GraphStep(g, visited=visited, frontier=[], current=u, path=path, distances=dist, code_line=10,
                                explanation=f"✅ Cél! Legrövidebb út: {' -> '.join(map(str, path))} költség={dist[target]}",
                                comparisons=comparisons, extra={"start": start, "target": target, "path": path, "dist": dict(dist), "found": True})
                return
            
            for v,w in g.nodes[u].neighbors:
                if dist[u]+w < dist[v]:
                    old = dist[v]
                    dist[v] = dist[u]+w
                    parent[v] = u
                    heapq.heappush(pq, (dist[v], v))
                    yield GraphStep(g, visited=visited, frontier=[n for _,n in pq], current=u, distances=dist, code_line=12,
                                    explanation=f"Relax: {u}->{v} ({w}) javít {old} -> {dist[v]}",
                                    comparisons=comparisons, extra={"start": start, "target": target, "dist": dict(dist), "edge": (u,v), "pq": list(pq)})
        
        yield GraphStep(g, visited=visited, frontier=[], current=None, distances=dist, code_line=15,
                        explanation="❌ Dijkstra vége", comparisons=comparisons, extra={"start": start, "target": target, "dist": dict(dist)})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class AStarPlugin(AlgorithmPluginBase):
    id = "astar"
    name = "A* - Heurisztikus útkeresés"
    description = "Dijkstra + heurisztika, játékokban, térképen"
    time_complexity = "O(E)"
    space_complexity = "O(V)"
    icon = "⭐"
    version = "1.1.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "graph"

    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("graph_size", "Gráf méret", "int", 5, 3, 8, description="Csomópontok / rács méret"))
        self.params.add(Param("density", "Sűrűség", "choice", "közepes", choices=["ritka", "közepes", "sűrű"], description="Élek sűrűsége"))
    
    def get_params(self):
        return self.params
    
    def set_param(self, pid, val):
        self.params.set(pid, val)
    

    codes = {
        "Python": """def astar(graf, start, cel, heurisztika):
    open_set=[(0,start)]
    g_score={node: float('inf') for node in graf}
    g_score[start]=0
    f_score={node: float('inf') for node in graf}
    f_score[start]=heurisztika(start,cel)
    parent={start: None}
    while open_set:
        _, u = heapq.heappop(open_set)
        if u==cel: break
        for v,w in graf[u].neighbors:
            tentative = g_score[u]+w
            if tentative < g_score[v]:
                parent[v]=u
                g_score[v]=tentative
                f_score[v]=tentative+heurisztika(v,cel)
                heapq.heappush(open_set,(f_score[v],v))
    return parent""",
        "C++": """void AStar(Graph& g, int start, int goal){
    auto heuristic = [&](int a, int b){ return abs(g.nodes[a].x-g.nodes[b].x)+abs(g.nodes[a].y-g.nodes[b].y); };
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> open;
    map<int,int> gScore, fScore; gScore[start]=0; fScore[start]=heuristic(start,goal);
    open.push({fScore[start], start});
    while(!open.empty()){
        auto [f,u]=open.top(); open.pop();
        if(u==goal) break;
        for(auto [v,w]: g.adj[u]){
            int tentative=gScore[u]+w;
            if(tentative<gScore[v]){
                gScore[v]=tentative; fScore[v]=tentative+heuristic(v,goal);
                open.push({fScore[v], v});
            }
        }
    }
}""",
        "C": "/* A* C - heurisztikával */\nint heuristic(int a, int b){return abs(x[a]-x[b])+abs(y[a]-y[b]);}\nvoid AStar(int g[][V], int start, int goal){int gScore[V], fScore[V]; for(int i=0;i<V;i++){gScore[i]=INF; fScore[i]=INF;} gScore[start]=0; fScore[start]=heuristic(start,goal); /* pq... */}",
        "BASIC": "FUNCTION Heuristic(a,b): Heuristic=ABS(x(a)-x(b))+ABS(y(a)-y(b)): END FUNCTION\nSUB AStar(start,goal)\n DIM gScore(V), fScore(V): gScore(start)=0: fScore(start)=Heuristic(start,goal)\n WHILE open NOT EMPTY\n  u=PopMin(open): IF u=goal THEN EXIT\n  FOR EACH v,w IN adj(u): tentative=gScore(u)+w: IF tentative<gScore(v) THEN gScore(v)=tentative: fScore(v)=tentative+Heuristic(v,goal): Push open, fScore(v), v\n WEND\nEND SUB",
        "Java": "void AStar(Graph g, int start, int goal){Function<Integer, Integer> h = (a)->Math.abs(g.nodes[a].x-g.nodes[goal].x)+Math.abs(g.nodes[a].y-g.nodes[goal].y); PriorityQueue<int[]> open=new PriorityQueue<>(Comparator.comparingInt(a->a[0])); Map<Integer,Integer> gScore=new HashMap<>(), fScore=new HashMap<>(); gScore.put(start,0); fScore.put(start,h.apply(start)); open.add(new int[]{fScore.get(start), start}); while(!open.isEmpty()){int u=open.poll()[1]; if(u==goal) break; for(int[] e: g.adj[u]){int v=e[0], w=e[1]; int tentative=gScore.get(u)+w; if(tentative<gScore.getOrDefault(v, INF)){gScore.put(v,tentative); fScore.put(v,tentative+h.apply(v)); open.add(new int[]{fScore.get(v),v});}}}}",
        "Pascal": "function Heuristic(a,b: Integer): Integer; begin Result:=Abs(x[a]-x[b])+Abs(y[a]-y[b]); end; procedure AStar(start,goal: Integer); var gScore,fScore: array of Integer; open: array of Integer; u,v,w: Integer; begin gScore[start]:=0; fScore[start]:=Heuristic(start,goal); Push(open,fScore[start],start); while not Empty(open) do begin u:=PopMin(open); if u=goal then Break; for v,w in adj[u] do begin if gScore[u]+w<gScore[v] then begin gScore[v]:=gScore[u]+w; fScore[v]:=gScore[v]+Heuristic(v,goal); Push(open,fScore[v],v); end; end; end; end;"
    }
    
    def get_steps(self, arr):
        g = Graph.create_pathfinding_grid(6)
        if not g.nodes:
            g = Graph.create_random_weighted(6)
        nodes = list(g.nodes.keys())
        if len(nodes) < 2:
            return
        start = nodes[0]
        target = nodes[-1]
        
        def heuristic(a,b):
            if a in g.nodes and b in g.nodes:
                return abs(g.nodes[a].x - g.nodes[b].x) + abs(g.nodes[a].y - g.nodes[b].y)
            return 0
        
        open_set = [(heuristic(start,target), start)]
        g_score = {node: float('inf') for node in g.nodes}
        g_score[start] = 0
        f_score = {node: float('inf') for node in g.nodes}
        f_score[start] = heuristic(start, target)
        parent = {start: None}
        visited = set()
        comparisons = 0
        
        yield GraphStep(g, visited=set(), frontier=[start], current=start, distances=g_score, code_line=3,
                        explanation=f"⭐ A* kezdés: start={start}, cél={target}, f={f_score[start]:.0f}",
                        comparisons=0, extra={"start": start, "target": target, "f_score": dict(f_score), "g_score": dict(g_score), "open": [start]})
        
        while open_set:
            f,u = heapq.heappop(open_set)
            comparisons+=1
            if u in visited:
                continue
            visited.add(u)
            yield GraphStep(g, visited=visited, frontier=[n for _,n in open_set], current=u, distances=g_score, code_line=8,
                            explanation=f"Kivesz: u={u} f={f:.0f} g={g_score[u]} h={f-g_score[u]:.0f}",
                            comparisons=comparisons, extra={"start": start, "target": target, "f_score": dict(f_score), "g_score": dict(g_score), "open": [n for _,n in open_set]})
            
            if u == target:
                path = []
                cur = target
                while cur is not None:
                    path.append(cur)
                    cur = parent.get(cur)
                path.reverse()
                yield GraphStep(g, visited=visited, frontier=[], current=u, path=path, distances=g_score, code_line=10,
                                explanation=f"✅ A* cél! Út: {' -> '.join(map(str, path))} költség={g_score[target]}",
                                comparisons=comparisons, extra={"start": start, "target": target, "path": path, "found": True, "g_score": dict(g_score)})
                return
            
            for v,w in g.nodes[u].neighbors:
                tentative = g_score[u] + w
                if tentative < g_score[v]:
                    parent[v] = u
                    g_score[v] = tentative
                    f_score[v] = tentative + heuristic(v, target)
                    heapq.heappush(open_set, (f_score[v], v))
                    yield GraphStep(g, visited=visited, frontier=[n for _,n in open_set], current=u, distances=g_score, code_line=13,
                                    explanation=f"Frissít: {u}->{v} g={tentative} f={f_score[v]:.0f}",
                                    comparisons=comparisons, extra={"start": start, "target": target, "edge": (u,v), "f_score": dict(f_score), "g_score": dict(g_score), "open": [n for _,n in open_set]})
        
        yield GraphStep(g, visited=visited, frontier=[], current=None, distances=g_score, code_line=15,
                        explanation="❌ A* vége", comparisons=comparisons, extra={"start": start, "target": target})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
