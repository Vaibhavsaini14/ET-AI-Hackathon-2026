import pickle
import os
import networkx as nx
from loguru import logger

GRAPH_PATH = "./knowledge_graph.pkl"

class KnowledgeGraphService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.graph = nx.DiGraph()
        self.load()
        self._initialized = True

    def add_extraction(self, extraction: dict) -> None:
        chunk_id = extraction.get("chunk_id")

        for entity in extraction.get("entities", []):
            name = entity["name"].strip()
            if not self.graph.has_node(name):
                self.graph.add_node(name, type=entity["type"], chunk_ids=[chunk_id])
            else:
                self.graph.nodes[name].setdefault("chunk_ids", [])
                if chunk_id not in self.graph.nodes[name]["chunk_ids"]:
                    self.graph.nodes[name]["chunk_ids"].append(chunk_id)

        for rel in extraction.get("relationships", []):
            src, tgt = rel["source"].strip(), rel["target"].strip()
            if not self.graph.has_node(src):
                self.graph.add_node(src, type="UNKNOWN", chunk_ids=[chunk_id])
            if not self.graph.has_node(tgt):
                self.graph.add_node(tgt, type="UNKNOWN", chunk_ids=[chunk_id])
            self.graph.add_edge(src, tgt, relation=rel["relation"], chunk_id=chunk_id)

        self.save()

    def get_neighbors(self, entity_name: str, hops: int = 1) -> dict:
        if entity_name not in self.graph:
            matches = [n for n in self.graph.nodes if entity_name.lower() in n.lower()]
            if not matches:
                return {"entity": entity_name, "found": False, "neighbors": []}
            entity_name = matches[0]

        visited = {entity_name}
        frontier = {entity_name}
        neighbors = []

        for _ in range(hops):
            next_frontier = set()
            for node in frontier:
                for succ in self.graph.successors(node):
                    edge = self.graph.get_edge_data(node, succ)
                    neighbors.append({
                        "from": node, "relation": edge["relation"], "to": succ,
                        "chunk_id": edge.get("chunk_id")
                    })
                    next_frontier.add(succ)
                for pred in self.graph.predecessors(node):
                    edge = self.graph.get_edge_data(pred, node)
                    neighbors.append({
                        "from": pred, "relation": edge["relation"], "to": node,
                        "chunk_id": edge.get("chunk_id")
                    })
                    next_frontier.add(pred)
            frontier = next_frontier - visited
            visited |= next_frontier

        return {"entity": entity_name, "found": True, "neighbors": neighbors}

    def get_relevant_chunk_ids(self, query_entities: list, hops: int = 1) -> set:
        chunk_ids = set()
        for ent in query_entities:
            result = self.get_neighbors(ent, hops=hops)
            for n in result["neighbors"]:
                if n.get("chunk_id"):
                    chunk_ids.add(n["chunk_id"])
        return chunk_ids

    def get_stats(self) -> dict:
        return {
            "total_entities": self.graph.number_of_nodes(),
            "total_relationships": self.graph.number_of_edges()
        }

    def save(self) -> None:
        with open(GRAPH_PATH, "wb") as f:
            pickle.dump(self.graph, f)

    def load(self) -> None:
        if os.path.exists(GRAPH_PATH):
            with open(GRAPH_PATH, "rb") as f:
                self.graph = pickle.load(f)
            logger.info(f"Knowledge graph loaded — {self.graph.number_of_nodes()} entities")