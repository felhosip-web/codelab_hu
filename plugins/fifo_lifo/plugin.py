# -*- coding: utf-8 -*-
from core.plugin_system import AlgorithmPluginBase
from core.dynamic_params import DynamicParams, Param
from core.step import VisualizationStep
from core.fifo_lifo import Stack, Queue, Deque, CircularQueue, PriorityQueue
import random

class FIFOStep(VisualizationStep):
    def __init__(self, structure=None, structure_type="stack", operation="", value=None,
                 top=None, front=None, rear=None,
                 code_line=0, explanation="", comparisons=0, extra=None):
        extra_dict = extra.copy() if extra else {}
        if structure is not None and "structure" not in extra_dict:
            extra_dict["structure"] = structure
        if structure_type and "structure_type" not in extra_dict:
            extra_dict["structure_type"] = structure_type
        if operation and "operation" not in extra_dict:
            extra_dict["operation"] = operation
        if value is not None and "value" not in extra_dict:
            extra_dict["value"] = value
        if top is not None and "top" not in extra_dict:
            extra_dict["top"] = top
        if front is not None and "front" not in extra_dict:
            extra_dict["front"] = front
        if rear is not None and "rear" not in extra_dict:
            extra_dict["rear"] = rear

        arr = structure if isinstance(structure, list) else []
        super().__init__(
            explanation=explanation,
            code_line=code_line,
            metrics={"comparisons": comparisons, "pass_num": comparisons},
            array=arr,
            key=value,
            extra=extra_dict
        )

class StackPlugin(AlgorithmPluginBase):
    id = "stack"
    name = "Verem - LIFO"
    description = "Last In First Out, push, pop, peek, verem"
    time_complexity = "O(1)"
    space_complexity = "O(n)"
    icon = "📚"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "fifo_lifo"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("ops", "Műveletek száma", "int", 8, 4, 12))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Verem - LIFO (Last In First Out)
# Olyan mint egy könyv torony: utoljára tettet veszed le először

stack = []  # Üres verem

# Push - rátol
stack.append(10)  # [10]
stack.append(20)  # [10,20]
stack.append(30)  # [10,20,30] top=30

# Peek - megnéz
top = stack[-1]  # 30, nem veszi le

# Pop - levesz
val = stack.pop()  # 30, [10,20]
val = stack.pop()  # 20, [10]

# Üres-e?
is_empty = len(stack)==0  # False

# Használat: függvényhívás verem, undo, zárójelezés ellenőrzés
# Példa: 3*(2+1) -> verem a zárójeleknek
""",
        "C++": "// Verem C++ - LIFO\n#include <stack>\nstack<int> s;\ns.push(10); // [10]\ns.push(20); // [10,20]\ns.push(30); // [10,20,30] top=30\nint top = s.top(); // 30\nint val = s.top(); s.pop(); // 30, [10,20]\nbool empty = s.empty();\n// Saját implementáció: vector vagy linked list\n// push O(1), pop O(1)",
        "C": "/* Verem C */\n#define MAX 100\nint stack[MAX]; int top=-1;\nvoid push(int x){ if(top<MAX-1) stack[++top]=x; }\nint pop(){ if(top>=0) return stack[top--]; return -1; }\nint peek(){ if(top>=0) return stack[top]; return -1; }\nint isEmpty(){ return top==-1; }\n// push(10) -> [10] top=0\n// push(20) -> [10,20] top=1\n// pop() -> 20 top=0",
        "BASIC": "DIM stack(100) AS INTEGER: top=-1\nSUB push(x AS INTEGER): top=top+1: stack(top)=x: END SUB\nFUNCTION pop() AS INTEGER: IF top>=0 THEN pop=stack(top): top=top-1: ELSE pop=-1: END FUNCTION\nFUNCTION peek() AS INTEGER: IF top>=0 THEN peek=stack(top): ELSE peek=-1: END FUNCTION\npush 10: push 20: ' [10,20] top=20\nPRINT pop(); ' 20",
        "Java": "// Verem Java - LIFO\nStack<Integer> s = new Stack<>();\ns.push(10); // [10]\ns.push(20); // [10,20]\ns.push(30); // [10,20,30]\nint top = s.peek(); // 30\nint val = s.pop(); // 30, [10,20]\nboolean empty = s.isEmpty();\n// Deque is használható: Deque<Integer> s = new ArrayDeque<>(); s.push(10);",
        "Pascal": "const MAX=100; var stack: array[0..MAX-1] of Integer; top: Integer; procedure push(x: Integer); begin if top<MAX-1 then begin Inc(top); stack[top]:=x; end; end; function pop: Integer; begin if top>=0 then begin pop:=stack[top]; Dec(top); end else pop:=-1; end; function peek: Integer; begin if top>=0 then peek:=stack[top] else peek:=-1; end; begin top:=-1; push(10); push(20); // [10,20]\nWriteLn(pop); // 20\nend;"
    }
    
    def get_steps(self, arr):
        ops = self.params.get("ops")
        stack = Stack()
        
        yield FIFOStep(structure=[], structure_type="stack", operation="init", code_line=1,
                       explanation=f"📚 Verem (LIFO) létrehozás: üres verem, Last In First Out",
                       comparisons=0, extra={"phase": "init", "stack": []})
        
        values = [random.randint(1, 50) for _ in range(ops)]
        
        # Push műveletek
        for i, val in enumerate(values[:ops//2]):
            stack.push(val)
            yield FIFOStep(structure=stack.items[:], structure_type="stack", operation="push", value=val, top=stack.peek(), code_line=3,
                           explanation=f"Push {val} -> verem: {stack.items} | Top: {stack.peek()} | Méret: {stack.size()}",
                           comparisons=i+1, extra={"phase": "push", "value": val, "stack": stack.items[:], "top": stack.peek()})
        
        # Peek
        yield FIFOStep(structure=stack.items[:], structure_type="stack", operation="peek", value=stack.peek(), top=stack.peek(), code_line=6,
                       explanation=f"Peek -> Top: {stack.peek()} | Verem marad: {stack.items}",
                       comparisons=ops//2+1, extra={"phase": "peek", "top": stack.peek(), "stack": stack.items[:]})
        
        # Pop műveletek
        for i in range(min(ops//2, stack.size())):
            val = stack.pop()
            yield FIFOStep(structure=stack.items[:], structure_type="stack", operation="pop", value=val, top=stack.peek(), code_line=8,
                           explanation=f"Pop -> {val} | Verem: {stack.items} | Top: {stack.peek() if not stack.is_empty() else 'üres'}",
                           comparisons=ops//2+2+i, extra={"phase": "pop", "value": val, "stack": stack.items[:], "top": stack.peek()})
        
        yield FIFOStep(structure=stack.items[:], structure_type="stack", operation="done", code_line=10,
                       explanation=f"✅ Verem kész: {stack.items} | LIFO: utoljára betett kerül ki először",
                       comparisons=ops, extra={"phase": "kesz", "stack": stack.items[:]})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class QueuePlugin(AlgorithmPluginBase):
    id = "queue"
    name = "Sor - FIFO"
    description = "First In First Out, enqueue, dequeue, sor"
    time_complexity = "O(1) / O(n)"
    space_complexity = "O(n)"
    icon = "🚶"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "fifo_lifo"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("ops", "Műveletek száma", "int", 8, 4, 12))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Sor - FIFO (First In First Out)
# Olyan mint egy sor a boltban: elsőnek jött megy ki elsőnek

from collections import deque

queue = deque()  # Üres sor

# Enqueue - sorba áll
queue.append(10)  # [10] rear=10
queue.append(20)  # [10,20] rear=20
queue.append(30)  # [10,20,30] rear=30 front=10

# Front - megnéz elejét
front = queue[0]  # 10

# Dequeue - kivesz elölről
val = queue.popleft()  # 10, [20,30] front=20
val = queue.popleft()  # 20, [30]

# Üres-e?
is_empty = len(queue)==0

# Használat: BFS, nyomtató sor, feladatok ütemezése
# Példa: nyomtató sorban 3 dokumentum, első nyomtatódik először
""",
        "C++": "// Sor C++ - FIFO\n#include <queue>\nqueue<int> q;\nq.push(10); // [10]\nq.push(20); // [10,20]\nq.push(30); // [10,20,30] front=10 rear=30\nint front = q.front(); // 10\nint val = q.front(); q.pop(); // 10, [20,30]\nbool empty = q.empty();\n// Saját: circular buffer vagy linked list\n// enqueue O(1), dequeue O(1) circular, O(n) sima listánál",
        "C": "/* Sor C */\n#define MAX 100\nint queue[MAX]; int front=-1, rear=-1;\nvoid enqueue(int x){ if(rear<MAX-1){ if(front==-1) front=0; queue[++rear]=x; } }\nint dequeue(){ if(front==-1 || front>rear) return -1; int val=queue[front++]; if(front>rear) front=rear=-1; return val; }\nint frontVal(){ if(front!=-1) return queue[front]; return -1; }\n// enqueue(10) -> [10] front=0 rear=0\n// enqueue(20) -> [10,20] front=0 rear=1\n// dequeue() -> 10 front=1",
        "BASIC": "DIM queue(100) AS INTEGER: front=-1: rear=-1\nSUB enqueue(x AS INTEGER): IF rear<100 THEN IF front=-1 THEN front=0: rear=rear+1: queue(rear)=x: END SUB\nFUNCTION dequeue() AS INTEGER: IF front<>-1 THEN dequeue=queue(front): front=front+1: IF front>rear THEN front=-1: rear=-1: ELSE dequeue=-1: END FUNCTION\nenqueue 10: enqueue 20: ' [10,20]\nPRINT dequeue(); ' 10",
        "Java": "// Sor Java - FIFO\nQueue<Integer> q = new LinkedList<>();\nq.add(10); // [10]\nq.add(20); // [10,20]\nq.add(30); // [10,20,30] front=10\nint front = q.peek(); // 10\nint val = q.poll(); // 10, [20,30]\nboolean empty = q.isEmpty();\n// ArrayDeque is jobb: Queue<Integer> q = new ArrayDeque<>();",
        "Pascal": "const MAX=100; var queue: array[0..MAX-1] of Integer; front, rear: Integer; procedure enqueue(x: Integer); begin if rear<MAX-1 then begin if front=-1 then front:=0; Inc(rear); queue[rear]:=x; end; end; function dequeue: Integer; begin if front<>-1 then begin dequeue:=queue[front]; Inc(front); if front>rear then begin front:=-1; rear:=-1; end; end else dequeue:=-1; end; begin front:=-1; rear:=-1; enqueue(10); enqueue(20); // [10,20]\nWriteLn(dequeue); // 10\nend;"
    }
    
    def get_steps(self, arr):
        ops = self.params.get("ops")
        queue = Queue()
        
        yield FIFOStep(structure=[], structure_type="queue", operation="init", code_line=1,
                       explanation=f"🚶 Sor (FIFO) létrehozás: üres sor, First In First Out",
                       comparisons=0, extra={"phase": "init", "queue": []})
        
        values = [random.randint(1, 50) for _ in range(ops)]
        
        for i, val in enumerate(values[:ops//2]):
            queue.enqueue(val)
            yield FIFOStep(structure=queue.items[:], structure_type="queue", operation="enqueue", value=val, front=queue.front(), code_line=3,
                           explanation=f"Enqueue {val} -> sor: {queue.items} | Front: {queue.front()} | Rear: {val}",
                           comparisons=i+1, extra={"phase": "enqueue", "value": val, "queue": queue.items[:], "front": queue.front()})
        
        yield FIFOStep(structure=queue.items[:], structure_type="queue", operation="front", value=queue.front(), front=queue.front(), code_line=6,
                       explanation=f"Front -> {queue.front()} | Sor marad: {queue.items}",
                       comparisons=ops//2+1, extra={"phase": "front", "front": queue.front(), "queue": queue.items[:]})
        
        for i in range(min(ops//2, queue.size())):
            val = queue.dequeue()
            yield FIFOStep(structure=queue.items[:], structure_type="queue", operation="dequeue", value=val, front=queue.front(), code_line=8,
                           explanation=f"Dequeue -> {val} | Sor: {queue.items} | Front: {queue.front() if not queue.is_empty() else 'üres'}",
                           comparisons=ops//2+2+i, extra={"phase": "dequeue", "value": val, "queue": queue.items[:], "front": queue.front()})
        
        yield FIFOStep(structure=queue.items[:], structure_type="queue", operation="done", code_line=10,
                       explanation=f"✅ Sor kész: {queue.items} | FIFO: elsőnek betett kerül ki először",
                       comparisons=ops, extra={"phase": "kesz", "queue": queue.items[:]})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class CircularQueuePlugin(AlgorithmPluginBase):
    id = "circular_queue"
    name = "Körkörös sor"
    description = "Körkörös buffer, front/rear forog, hatékony"
    time_complexity = "O(1)"
    space_complexity = "O(n)"
    icon = "🔄"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "fifo_lifo"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("capacity", "Kapacitás", "int", 5, 3, 8))
        self.params.add(Param("ops", "Műveletek", "int", 10, 5, 15))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Körkörös sor - Circular Queue
# Fix méret, front/rear körbe forog, nincs eltolás

class CircularQueue:
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.queue = [None]*capacity
        self.front = -1
        self.rear = -1
    
    def enqueue(self, item):
        if self.is_full():
            return False
        if self.is_empty():
            self.front = 0
        self.rear = (self.rear + 1) % self.capacity
        self.queue[self.rear] = item
        return True
    
    def dequeue(self):
        if self.is_empty():
            return None
        item = self.queue[self.front]
        self.queue[self.front] = None
        if self.front == self.rear:
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.capacity
        return item
    
    def is_full(self):
        return (self.rear + 1) % self.capacity == self.front

# Példa kapacitás 5:
# enqueue 10: [10,None,None,None,None] front=0 rear=0
# enqueue 20: [10,20,None,None,None] front=0 rear=1
# dequeue: [None,20,None,None,None] front=1 rear=1
# enqueue 30: [None,20,30,None,None] front=1 rear=2
# Körbeforgás: ha rear a végén, következő 0-ra megy!
""",
        "C++": "// Körkörös sor C++\nclass CircularQueue{int capacity; vector<int> q; int front, rear; public: CircularQueue(int cap): capacity(cap), q(cap, -1), front(-1), rear(-1) {} bool enqueue(int x){ if((rear+1)%capacity==front) return false; if(front==-1) front=0; rear=(rear+1)%capacity; q[rear]=x; return true; } int dequeue(){ if(front==-1) return -1; int val=q[front]; q[front]=-1; if(front==rear) front=rear=-1; else front=(front+1)%capacity; return val; } };",
        "C": "/* Körkörös sor C */\n#define CAP 5\nint queue[CAP]; int front=-1, rear=-1;\nint enqueue(int x){ if((rear+1)%CAP==front) return 0; if(front==-1) front=0; rear=(rear+1)%CAP; queue[rear]=x; return 1; }\nint dequeue(){ if(front==-1) return -1; int val=queue[front]; queue[front]=-1; if(front==rear) front=rear=-1; else front=(front+1)%CAP; return val; }",
        "BASIC": "CONST CAP=5: DIM queue(CAP) AS INTEGER: front=-1: rear=-1\nFUNCTION enqueue(x AS INTEGER) AS INTEGER: IF (rear+1) MOD CAP=front THEN RETURN 0: IF front=-1 THEN front=0: rear=(rear+1) MOD CAP: queue(rear)=x: RETURN 1: END FUNCTION\nFUNCTION dequeue() AS INTEGER: IF front=-1 THEN RETURN -1: val=queue(front): queue(front)=-1: IF front=rear THEN front=-1: rear=-1: ELSE front=(front+1) MOD CAP: RETURN val: END FUNCTION",
        "Java": "// Körkörös sor Java\nclass CircularQueue{int capacity; int[] q; int front, rear; CircularQueue(int cap){ capacity=cap; q=new int[cap]; front=rear=-1; } boolean enqueue(int x){ if((rear+1)%capacity==front) return false; if(front==-1) front=0; rear=(rear+1)%capacity; q[rear]=x; return true; } int dequeue(){ if(front==-1) return -1; int val=q[front]; q[front]=-1; if(front==rear) front=rear=-1; else front=(front+1)%capacity; return val; } }",
        "Pascal": "const CAP=5; var queue: array[0..CAP-1] of Integer; front, rear: Integer; function enqueue(x: Integer): Boolean; begin if (rear+1) mod CAP=front then enqueue:=False else begin if front=-1 then front:=0; rear:=(rear+1) mod CAP; queue[rear]:=x; enqueue:=True; end; end; function dequeue: Integer; var val: Integer; begin if front=-1 then dequeue:=-1 else begin val:=queue[front]; queue[front]:=-1; if front=rear then begin front:=-1; rear:=-1; end else front:=(front+1) mod CAP; dequeue:=val; end; end;"
    }
    
    def get_steps(self, arr):
        cap = self.params.get("capacity")
        ops = self.params.get("ops")
        cq = CircularQueue(capacity=cap)
        
        yield FIFOStep(structure=cq.queue[:], structure_type="circular", operation="init", front=cq.front, rear=cq.rear, code_line=1,
                       explanation=f"🔄 Körkörös sor: kapacitás {cap}, üres",
                       comparisons=0, extra={"phase": "init", "queue": cq.queue[:], "front": cq.front, "rear": cq.rear, "capacity": cap})
        
        values = [random.randint(1, 50) for _ in range(ops)]
        
        for i, val in enumerate(values):
            if i % 3 != 2:  # 2 enqueue, 1 dequeue minta
                success = cq.enqueue(val)
                if success:
                    yield FIFOStep(structure=cq.queue[:], structure_type="circular", operation="enqueue", value=val, front=cq.front, rear=cq.rear, code_line=8,
                                   explanation=f"Enqueue {val} -> {cq.queue} | front={cq.front} rear={cq.rear} | size={cq.size()}",
                                   comparisons=i+1, extra={"phase": "enqueue", "value": val, "queue": cq.queue[:], "front": cq.front, "rear": cq.rear})
                else:
                    yield FIFOStep(structure=cq.queue[:], structure_type="circular", operation="full", value=val, front=cq.front, rear=cq.rear, code_line=12,
                                   explanation=f"Full! Nem fér {val} -> {cq.queue} | front={cq.front} rear={cq.rear}",
                                   comparisons=i+1, extra={"phase": "full", "queue": cq.queue[:]})
            else:
                if not cq.is_empty():
                    removed = cq.dequeue()
                    yield FIFOStep(structure=cq.queue[:], structure_type="circular", operation="dequeue", value=removed, front=cq.front, rear=cq.rear, code_line=15,
                                   explanation=f"Dequeue -> {removed} | {cq.queue} | front={cq.front} rear={cq.rear}",
                                   comparisons=i+1, extra={"phase": "dequeue", "value": removed, "queue": cq.queue[:], "front": cq.front, "rear": cq.rear})
        
        yield FIFOStep(structure=cq.queue[:], structure_type="circular", operation="done", front=cq.front, rear=cq.rear, code_line=20,
                       explanation=f"✅ Körkörös kész: {cq.queue} | front={cq.front} rear={cq.rear} | Körbeforgás: (rear+1)%cap",
                       comparisons=ops, extra={"phase": "kesz", "queue": cq.queue[:]})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])

class DequePlugin(AlgorithmPluginBase):
    id = "deque"
    name = "Deque - kétvégű sor"
    description = "Double Ended Queue, mindkét végén lehet"
    time_complexity = "O(1)"
    space_complexity = "O(n)"
    icon = "↔️"
    version = "1.0.0"
    api_version_required = "1.0.0"
    author = "CodeLab HU Core"
    plugin_type = "fifo_lifo"
    
    def __init__(self):
        self.params = DynamicParams()
        self.params.add(Param("ops", "Műveletek", "int", 8, 4, 12))
    
    def get_params(self): return self.params
    def set_param(self, pid, val): self.params.set(pid, val)
    
    codes = {
        "Python": """# Deque - kétvégű sor
# Mindkét végén lehet hozzáadni és kivenni

from collections import deque

dq = deque()

# Hozzáadás
dq.append(10)        # Jobbra: [10]
dq.append(20)        # Jobbra: [10,20]
dq.appendleft(5)     # Balra: [5,10,20]
dq.appendleft(1)     # Balra: [1,5,10,20]

# Kivétel
val = dq.pop()       # Jobbról: 20 -> [1,5,10]
val = dq.popleft()   # Balról: 1 -> [5,10]

# Használat: palindrom ellenőrzés, sliding window, undo/redo mindkét irány
# Példa: [1,5,10] -> elölről és hátulról is elérhető
""",
        "C++": "// Deque C++\n#include <deque>\ndeque<int> dq;\ndq.push_back(10); // [10]\ndq.push_back(20); // [10,20]\ndq.push_front(5); // [5,10,20]\ndq.push_front(1); // [1,5,10,20]\nint val = dq.back(); dq.pop_back(); // 20 -> [1,5,10]\nval = dq.front(); dq.pop_front(); // 1 -> [5,10]\n// O(1) mindkét végén",
        "C": "/* Deque C - dupla láncolt lista vagy körkörös */\n// Egyszerű: front és rear mindkét irányban mozgatható\n// add_front: front = (front-1+CAP)%CAP\n// add_rear: rear = (rear+1)%CAP\n// remove_front: front = (front+1)%CAP\n// remove_rear: rear = (rear-1+CAP)%CAP",
        "BASIC": "DIM dq(100) AS INTEGER: front=50: rear=50\nSUB add_front(x): front=front-1: dq(front)=x: END SUB\nSUB add_rear(x): dq(rear)=x: rear=rear+1: END SUB\nFUNCTION remove_front(): IF front<rear THEN remove_front=dq(front): front=front+1: END FUNCTION\nFUNCTION remove_rear(): IF front<rear THEN rear=rear-1: remove_rear=dq(rear): END FUNCTION",
        "Java": "// Deque Java\nDeque<Integer> dq = new ArrayDeque<>();\ndq.addLast(10); // [10]\ndq.addLast(20); // [10,20]\ndq.addFirst(5); // [5,10,20]\ndq.addFirst(1); // [1,5,10,20]\nint val = dq.removeLast(); // 20 -> [1,5,10]\nval = dq.removeFirst(); // 1 -> [5,10]\n// O(1)",
        "Pascal": "var dq: array[0..99] of Integer; front, rear: Integer; procedure add_front(x: Integer); begin Dec(front); dq[front]:=x; end; procedure add_rear(x: Integer); begin dq[rear]:=x; Inc(rear); end; function remove_front: Integer; begin if front<rear then begin remove_front:=dq[front]; Inc(front); end else remove_front:=-1; end; function remove_rear: Integer; begin if front<rear then begin Dec(rear); remove_rear:=dq[rear]; end else remove_rear:=-1; end;"
    }
    
    def get_steps(self, arr):
        ops = self.params.get("ops")
        dq = Deque()
        
        yield FIFOStep(structure=[], structure_type="deque", operation="init", code_line=1,
                       explanation=f"↔️ Deque: kétvégű sor, mindkét végén lehet",
                       comparisons=0, extra={"phase": "init", "deque": []})
        
        values = [random.randint(1, 50) for _ in range(ops)]
        
        for i, val in enumerate(values):
            if i % 4 == 0:
                dq.add_rear(val)
                yield FIFOStep(structure=dq.items[:], structure_type="deque", operation="add_rear", value=val, code_line=5,
                               explanation=f"Add rear {val} -> {dq.items}",
                               comparisons=i+1, extra={"phase": "add_rear", "value": val, "deque": dq.items[:]})
            elif i % 4 == 1:
                dq.add_front(val)
                yield FIFOStep(structure=dq.items[:], structure_type="deque", operation="add_front", value=val, code_line=6,
                               explanation=f"Add front {val} -> {dq.items}",
                               comparisons=i+1, extra={"phase": "add_front", "value": val, "deque": dq.items[:]})
            elif i % 4 == 2:
                if not dq.is_empty():
                    removed = dq.remove_front()
                    yield FIFOStep(structure=dq.items[:], structure_type="deque", operation="remove_front", value=removed, code_line=9,
                                   explanation=f"Remove front -> {removed} | {dq.items}",
                                   comparisons=i+1, extra={"phase": "remove_front", "value": removed, "deque": dq.items[:]})
            else:
                if not dq.is_empty():
                    removed = dq.remove_rear()
                    yield FIFOStep(structure=dq.items[:], structure_type="deque", operation="remove_rear", value=removed, code_line=10,
                                   explanation=f"Remove rear -> {removed} | {dq.items}",
                                   comparisons=i+1, extra={"phase": "remove_rear", "value": removed, "deque": dq.items[:]})
        
        yield FIFOStep(structure=dq.items[:], structure_type="deque", operation="done", code_line=12,
                       explanation=f"✅ Deque kész: {dq.items} | Mindkét végén O(1)",
                       comparisons=ops, extra={"phase": "kesz", "deque": dq.items[:]})
    
    def get_code(self, lang): return self.codes.get(lang, self.codes["Python"])
