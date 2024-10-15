from vk_friends_graph import VkGraph
import networkx as nx
import json, asyncio
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt


class GraphCenter():
    def __init__(
            self, 
            find_closeness_centrality=True, 
            find_betweenness_centrality=True,
            find_eigenvector_centrality=True,
            draw_graph=True,
            generate_new_graph=False
            ):
        
        self.find_closeness_centrality = find_closeness_centrality
        self.find_betweenness_centrality = find_betweenness_centrality
        self.draw_graph = draw_graph
        self.find_eigenvector_centrality = find_eigenvector_centrality

        if generate_new_graph:
            new_graph = VkGraph(write_json=True)

        self._get_friends_graph()
        asyncio.run(self._start())
        self._end()


    def _get_friends_graph(self):
        with open('friends.json', 'r') as json_file:
            friends_graph = json.load(json_file)

        self.graph = nx.Graph()

        for person, friends in friends_graph.items():
            for friend in friends:
                self.graph.add_edge(person, str(friend))

        print(f"Количество узлов: {self.graph.number_of_nodes()}")
        print(f"Количество рёбер: {self.graph.number_of_edges()}")
        print()


    async def _start(self):
        tasks = []

        if self.find_closeness_centrality:
            tasks.append(self._run_in_executor(self._find_closeness_centrality))

        if self.find_betweenness_centrality:
            tasks.append(self._run_in_executor(self._find_betweenness_centrality))

        if self.find_eigenvector_centrality:
            tasks.append(self._run_in_executor(self._find_eigenvector_centrality))

        await asyncio.gather(*tasks)


    async def _run_in_executor(self, func):
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, func)


    def _end(self):
        if self.find_closeness_centrality:
            max_closeness_node = max(self.closeness_centrality, key=self.closeness_centrality.get)
            print("Максимальная центральность по близости:")
            print(f"ID узла: {max_closeness_node}, Значение: {self.closeness_centrality[max_closeness_node]}")
            print()

        if self.find_betweenness_centrality:
            max_betweenness_node = max(self.betweenness_centrality, key=self.betweenness_centrality.get)
            print("Максимальная центральность по посредничеству:")
            print(f"ID узла: {max_betweenness_node}, Значение: {self.betweenness_centrality[max_betweenness_node]}")
            print()

        if self.find_eigenvector_centrality:
            max_eigenvector_node = max(self.eigenvector_centrality, key=self.eigenvector_centrality.get)
            print("Максимальная центральность по собственному значению:")
            print(f"ID узла: {max_eigenvector_node}, Значение: {self.eigenvector_centrality[max_eigenvector_node]}")
            print()

        if self.draw_graph:
            self._draw_graph(self.graph)


    @staticmethod
    def _draw_graph(graph):
        pos = nx.spring_layout(graph)
        node_color = '#FF9771'
        
        nx.draw_networkx_nodes(graph, pos, node_color=node_color, node_size=40, node_shape='o')
        nx.draw_networkx_edges(graph, pos, width=0.5, edge_color='gray')

        plt.axis('off')
        plt.show()


    def _find_closeness_centrality(self):
        self.closeness_centrality = nx.closeness_centrality(self.graph)


    def _find_betweenness_centrality(self):
        self.betweenness_centrality = nx.betweenness_centrality(self.graph)


    def _find_eigenvector_centrality(self):
        self.eigenvector_centrality = nx.eigenvector_centrality(self.graph, max_iter=500)


if __name__ == "__main__":
    graph = GraphCenter(draw_graph=True, generate_new_graph=False)
