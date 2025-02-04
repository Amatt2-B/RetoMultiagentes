using UnityEngine;

public class Spawner : MonoBehaviour
{
    public GameObject agentPrefab; // El prefab del agente
    public int numAgents = 10;    // Número de agentes a spawnear
    public float gridWidth = 10f; // Ancho del grid
    public float gridHeight = 10f; // Altura del grid
    public float spawnInterval = 2f; // Intervalo de spawn en segundos

    private float lastSpawnTime = 0f;

    void Update()
    {
        // Si ha pasado el intervalo de tiempo, spawn un nuevo agente
        if (Time.time - lastSpawnTime >= spawnInterval)
        {
            SpawnAgentOnEdge(); // Llamamos a una función para hacer el spawn en las orillas
            lastSpawnTime = Time.time;
        }
    }

    void SpawnAgentOnEdge()
    {
        // Elegimos un borde aleatorio (orilla)
        int edge = Random.Range(0, 4); // 0: arriba, 1: abajo, 2: izquierda, 3: derecha
        Vector3 spawnPosition = Vector3.zero;

        switch (edge)
        {
            case 0: // Arriba
                spawnPosition = new Vector3(Random.Range(0, gridWidth), 0, gridHeight);
                break;
            case 1: // Abajo
                spawnPosition = new Vector3(Random.Range(0, gridWidth), 0, 0);
                break;
            case 2: // Izquierda
                spawnPosition = new Vector3(0, 0, Random.Range(0, gridHeight));
                break;
            case 3: // Derecha
                spawnPosition = new Vector3(gridWidth, 0, Random.Range(0, gridHeight));
                break;
        }

        // Crear el nuevo agente en la posición determinada
        GameObject newAgent = Instantiate(agentPrefab, spawnPosition, Quaternion.identity);

        // Inicializar el agente (esto depende de la implementación de tu agente)
        newAgent.GetComponent<Agent>().Init(GetNextAgentId(), spawnPosition);
    }

    // Método para generar un ID único para cada agente
    int GetNextAgentId()
    {
        return Random.Range(1000, 9999); // Aquí puedes implementar tu lógica de IDs únicos
    }
}
