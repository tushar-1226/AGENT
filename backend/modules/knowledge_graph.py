"""
Team Knowledge Graph
Build organizational knowledge base and expert recommendation system
"""
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import json
from collections import defaultdict
import hashlib


class NodeType(Enum):
    """Types of nodes in knowledge graph"""
    PERSON = "person"
    SKILL = "skill"
    PROJECT = "project"
    DOCUMENT = "document"
    CODE_MODULE = "code_module"
    CONCEPT = "concept"
    TOOL = "tool"
    QUESTION = "question"
    ANSWER = "answer"


class RelationType(Enum):
    """Types of relationships between nodes"""
    HAS_SKILL = "has_skill"
    WORKED_ON = "worked_on"
    CREATED = "created"
    CONTRIBUTED_TO = "contributed_to"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    ANSWERED = "answered"
    ASKED = "asked"
    USES = "uses"
    EXPERT_IN = "expert_in"


@dataclass
class Node:
    """Represents a node in the knowledge graph"""
    id: str
    type: NodeType
    name: str
    properties: Dict[str, Any]
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class Edge:
    """Represents an edge (relationship) in the knowledge graph"""
    id: str
    source_id: str
    target_id: str
    type: RelationType
    weight: float = 1.0
    properties: Dict[str, Any] = None
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.properties is None:
            self.properties = {}


class KnowledgeGraph:
    """Core knowledge graph implementation"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.adjacency_list: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)
    
    def add_node(self, node: Node) -> bool:
        """Add a node to the graph"""
        if node.id in self.nodes:
            return False
        
        self.nodes[node.id] = node
        return True
    
    def add_edge(self, edge: Edge) -> bool:
        """Add an edge to the graph"""
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            return False
        
        self.edges[edge.id] = edge
        self.adjacency_list[edge.source_id].append(edge.target_id)
        self.reverse_adjacency[edge.target_id].append(edge.source_id)
        return True
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, edge_type: Optional[RelationType] = None) -> List[Node]:
        """Get neighboring nodes"""
        neighbors = []
        
        for target_id in self.adjacency_list.get(node_id, []):
            # Filter by edge type if specified
            if edge_type:
                edge = next((e for e in self.edges.values() 
                           if e.source_id == node_id and e.target_id == target_id 
                           and e.type == edge_type), None)
                if edge:
                    neighbors.append(self.nodes[target_id])
            else:
                neighbors.append(self.nodes[target_id])
        
        return neighbors
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> List[str]:
        """Find path between two nodes using BFS"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        
        queue = [(start_id, [start_id])]
        visited = {start_id}
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current_id == end_id:
                return path
            
            for neighbor_id in self.adjacency_list.get(current_id, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return []
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> Dict:
        """Get subgraph around a node"""
        subgraph_nodes = set()
        subgraph_edges = []
        
        queue = [(node_id, 0)]
        visited = {node_id}
        
        while queue:
            current_id, current_depth = queue.pop(0)
            subgraph_nodes.add(current_id)
            
            if current_depth < depth:
                for neighbor_id in self.adjacency_list.get(current_id, []):
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append((neighbor_id, current_depth + 1))
                    
                    # Add edge
                    edge = next((e for e in self.edges.values() 
                               if e.source_id == current_id and e.target_id == neighbor_id), None)
                    if edge:
                        subgraph_edges.append(edge)
        
        return {
            'nodes': [asdict(self.nodes[nid]) for nid in subgraph_nodes],
            'edges': [asdict(e) for e in subgraph_edges]
        }


class ExpertFinder:
    """Find experts on specific topics"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph
    
    def find_experts(self, topic: str, limit: int = 5) -> List[Dict]:
        """Find experts on a topic"""
        experts = []
        
        # Find skill/concept nodes matching the topic
        topic_nodes = [
            node for node in self.graph.nodes.values()
            if node.type in [NodeType.SKILL, NodeType.CONCEPT] 
            and topic.lower() in node.name.lower()
        ]
        
        # Find people connected to these topics
        expert_scores = defaultdict(float)
        
        for topic_node in topic_nodes:
            # Find people with this skill
            people = self.graph.get_neighbors(topic_node.id, RelationType.HAS_SKILL)
            
            for person in people:
                if person.type == NodeType.PERSON:
                    # Calculate expertise score
                    score = self._calculate_expertise_score(person.id, topic_node.id)
                    expert_scores[person.id] += score
        
        # Sort by score
        sorted_experts = sorted(expert_scores.items(), key=lambda x: x[1], reverse=True)
        
        for person_id, score in sorted_experts[:limit]:
            person = self.graph.get_node(person_id)
            experts.append({
                'id': person_id,
                'name': person.name,
                'expertise_score': score,
                'skills': [n.name for n in self.graph.get_neighbors(person_id, RelationType.HAS_SKILL)],
                'projects': [n.name for n in self.graph.get_neighbors(person_id, RelationType.WORKED_ON)]
            })
        
        return experts
    
    def _calculate_expertise_score(self, person_id: str, topic_id: str) -> float:
        """Calculate expertise score"""
        score = 1.0
        
        # Factor in number of projects
        projects = self.graph.get_neighbors(person_id, RelationType.WORKED_ON)
        score += len(projects) * 0.5
        
        # Factor in contributions
        contributions = self.graph.get_neighbors(person_id, RelationType.CONTRIBUTED_TO)
        score += len(contributions) * 0.3
        
        # Factor in answered questions
        answers = self.graph.get_neighbors(person_id, RelationType.ANSWERED)
        score += len(answers) * 0.2
        
        return score
    
    def recommend_collaborators(self, person_id: str, limit: int = 5) -> List[Dict]:
        """Recommend potential collaborators"""
        person = self.graph.get_node(person_id)
        if not person:
            return []
        
        # Get person's skills
        skills = self.graph.get_neighbors(person_id, RelationType.HAS_SKILL)
        
        # Find people with complementary or overlapping skills
        collaborator_scores = defaultdict(float)
        
        for skill in skills:
            # Find others with this skill
            others = self.graph.get_neighbors(skill.id, RelationType.HAS_SKILL)
            
            for other in others:
                if other.id != person_id and other.type == NodeType.PERSON:
                    collaborator_scores[other.id] += 1.0
        
        # Sort and return top collaborators
        sorted_collaborators = sorted(collaborator_scores.items(), 
                                     key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for collab_id, score in sorted_collaborators[:limit]:
            collab = self.graph.get_node(collab_id)
            recommendations.append({
                'id': collab_id,
                'name': collab.name,
                'compatibility_score': score,
                'shared_skills': score,
                'skills': [n.name for n in self.graph.get_neighbors(collab_id, RelationType.HAS_SKILL)]
            })
        
        return recommendations


class KnowledgeCapture:
    """Capture and store team knowledge"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph
        self.interaction_log = []
    
    def capture_interaction(self, interaction: Dict) -> str:
        """Capture team interaction (chat, commit, review, etc.)"""
        interaction_id = self._generate_id(interaction)
        
        # Extract entities from interaction
        entities = self._extract_entities(interaction)
        
        # Add nodes and edges to graph
        for entity in entities:
            node = Node(
                id=entity['id'],
                type=NodeType[entity['type']],
                name=entity['name'],
                properties=entity.get('properties', {})
            )
            self.graph.add_node(node)
        
        # Create relationships
        relationships = self._extract_relationships(interaction, entities)
        for rel in relationships:
            edge = Edge(
                id=self._generate_id(rel),
                source_id=rel['source'],
                target_id=rel['target'],
                type=RelationType[rel['type']],
                weight=rel.get('weight', 1.0)
            )
            self.graph.add_edge(edge)
        
        self.interaction_log.append({
            'id': interaction_id,
            'timestamp': datetime.now().isoformat(),
            'interaction': interaction
        })
        
        return interaction_id
    
    def _extract_entities(self, interaction: Dict) -> List[Dict]:
        """Extract entities from interaction"""
        entities = []
        
        # Extract person
        if 'user' in interaction:
            entities.append({
                'id': f"person_{interaction['user']}",
                'type': 'PERSON',
                'name': interaction['user'],
                'properties': {}
            })
        
        # Extract concepts from content
        if 'content' in interaction:
            # Simple keyword extraction (in production, use NLP)
            keywords = self._extract_keywords(interaction['content'])
            for keyword in keywords:
                entities.append({
                    'id': f"concept_{keyword}",
                    'type': 'CONCEPT',
                    'name': keyword,
                    'properties': {}
                })
        
        return entities
    
    def _extract_relationships(self, interaction: Dict, entities: List[Dict]) -> List[Dict]:
        """Extract relationships from interaction"""
        relationships = []
        
        # Create relationships between person and concepts
        person_entities = [e for e in entities if e['type'] == 'PERSON']
        concept_entities = [e for e in entities if e['type'] == 'CONCEPT']
        
        for person in person_entities:
            for concept in concept_entities:
                relationships.append({
                    'source': person['id'],
                    'target': concept['id'],
                    'type': 'RELATED_TO',
                    'weight': 1.0
                })
        
        return relationships
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simplified)"""
        # In production, use NLP libraries like spaCy
        words = text.lower().split()
        # Filter common words and return unique keywords
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if w not in common_words and len(w) > 3]
        return list(set(keywords[:5]))  # Return top 5 unique keywords
    
    def _generate_id(self, data: Dict) -> str:
        """Generate unique ID"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()


class TribalKnowledge:
    """Preserve institutional/tribal knowledge"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph
        self.knowledge_base = []
    
    def capture_decision(self, decision: Dict) -> str:
        """Capture architectural or technical decision"""
        decision_id = f"decision_{datetime.now().timestamp()}"
        
        node = Node(
            id=decision_id,
            type=NodeType.DOCUMENT,
            name=decision.get('title', 'Untitled Decision'),
            properties={
                'type': 'decision',
                'context': decision.get('context', ''),
                'decision': decision.get('decision', ''),
                'rationale': decision.get('rationale', ''),
                'consequences': decision.get('consequences', []),
                'alternatives': decision.get('alternatives', [])
            }
        )
        
        self.graph.add_node(node)
        
        # Link to people involved
        for person_name in decision.get('participants', []):
            person_id = f"person_{person_name}"
            edge = Edge(
                id=f"edge_{decision_id}_{person_id}",
                source_id=person_id,
                target_id=decision_id,
                type=RelationType.CONTRIBUTED_TO
            )
            self.graph.add_edge(edge)
        
        return decision_id
    
    def capture_lesson_learned(self, lesson: Dict) -> str:
        """Capture lessons learned"""
        lesson_id = f"lesson_{datetime.now().timestamp()}"
        
        node = Node(
            id=lesson_id,
            type=NodeType.DOCUMENT,
            name=lesson.get('title', 'Untitled Lesson'),
            properties={
                'type': 'lesson',
                'situation': lesson.get('situation', ''),
                'action': lesson.get('action', ''),
                'result': lesson.get('result', ''),
                'lesson': lesson.get('lesson', ''),
                'tags': lesson.get('tags', [])
            }
        )
        
        self.graph.add_node(node)
        self.knowledge_base.append(lesson)
        
        return lesson_id
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """Search tribal knowledge"""
        results = []
        
        # Search in nodes
        for node in self.graph.nodes.values():
            if node.type == NodeType.DOCUMENT:
                # Simple text matching (in production, use semantic search)
                if query.lower() in node.name.lower():
                    results.append({
                        'id': node.id,
                        'title': node.name,
                        'type': node.properties.get('type'),
                        'relevance': 1.0,
                        'content': node.properties
                    })
        
        return results


class TeamKnowledgeGraph:
    """Main team knowledge graph system"""
    
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.expert_finder = ExpertFinder(self.graph)
        self.knowledge_capture = KnowledgeCapture(self.graph)
        self.tribal_knowledge = TribalKnowledge(self.graph)
    
    def add_team_member(self, name: str, skills: List[str], 
                       projects: List[str] = None) -> str:
        """Add a team member to the knowledge graph"""
        person_id = f"person_{name}"
        
        # Create person node
        person_node = Node(
            id=person_id,
            type=NodeType.PERSON,
            name=name,
            properties={'role': 'developer'}
        )
        self.graph.add_node(person_node)
        
        # Add skills
        for skill in skills:
            skill_id = f"skill_{skill}"
            skill_node = Node(
                id=skill_id,
                type=NodeType.SKILL,
                name=skill,
                properties={}
            )
            self.graph.add_node(skill_node)
            
            # Create HAS_SKILL relationship
            edge = Edge(
                id=f"edge_{person_id}_{skill_id}",
                source_id=person_id,
                target_id=skill_id,
                type=RelationType.HAS_SKILL
            )
            self.graph.add_edge(edge)
        
        # Add projects
        if projects:
            for project in projects:
                project_id = f"project_{project}"
                project_node = Node(
                    id=project_id,
                    type=NodeType.PROJECT,
                    name=project,
                    properties={}
                )
                self.graph.add_node(project_node)
                
                # Create WORKED_ON relationship
                edge = Edge(
                    id=f"edge_{person_id}_{project_id}",
                    source_id=person_id,
                    target_id=project_id,
                    type=RelationType.WORKED_ON
                )
                self.graph.add_edge(edge)
        
        return person_id
    
    def find_expert(self, topic: str) -> List[Dict]:
        """Find experts on a topic"""
        return self.expert_finder.find_experts(topic)
    
    def get_recommendations(self, person_id: str) -> Dict:
        """Get recommendations for a person"""
        return {
            'collaborators': self.expert_finder.recommend_collaborators(person_id),
            'related_projects': self._get_related_projects(person_id),
            'learning_opportunities': self._get_learning_opportunities(person_id)
        }
    
    def _get_related_projects(self, person_id: str) -> List[Dict]:
        """Get related projects"""
        person = self.graph.get_node(person_id)
        if not person:
            return []
        
        skills = self.graph.get_neighbors(person_id, RelationType.HAS_SKILL)
        related_projects = set()
        
        for skill in skills:
            # Find projects using this skill
            projects = self.graph.get_neighbors(skill.id, RelationType.USES)
            related_projects.update(p.id for p in projects)
        
        return [
            {'id': pid, 'name': self.graph.get_node(pid).name}
            for pid in related_projects
        ]
    
    def _get_learning_opportunities(self, person_id: str) -> List[Dict]:
        """Suggest learning opportunities"""
        # Find skills of collaborators
        collaborators = self.expert_finder.recommend_collaborators(person_id, limit=10)
        
        person_skills = {s.name for s in self.graph.get_neighbors(person_id, RelationType.HAS_SKILL)}
        suggested_skills = set()
        
        for collab in collaborators:
            collab_skills = set(collab['skills'])
            new_skills = collab_skills - person_skills
            suggested_skills.update(new_skills)
        
        return [
            {'skill': skill, 'reason': 'Popular among your collaborators'}
            for skill in list(suggested_skills)[:5]
        ]
    
    def export_graph(self) -> Dict:
        """Export knowledge graph"""
        return {
            'nodes': [asdict(node) for node in self.graph.nodes.values()],
            'edges': [asdict(edge) for edge in self.graph.edges.values()],
            'statistics': {
                'total_nodes': len(self.graph.nodes),
                'total_edges': len(self.graph.edges),
                'node_types': self._count_node_types(),
                'edge_types': self._count_edge_types()
            }
        }
    
    def _count_node_types(self) -> Dict:
        """Count nodes by type"""
        counts = defaultdict(int)
        for node in self.graph.nodes.values():
            counts[node.type.value] += 1
        return dict(counts)
    
    def _count_edge_types(self) -> Dict:
        """Count edges by type"""
        counts = defaultdict(int)
        for edge in self.graph.edges.values():
            counts[edge.type.value] += 1
        return dict(counts)
