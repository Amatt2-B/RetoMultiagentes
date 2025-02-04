using System.Collections.Generic;
using UnityEngine;

public class Agent : MonoBehaviour
{
    public int id { get; private set; }
    private Vector3 moveTo;
    private Vector3 oldPos;
    private float interpolationSpeed = 5.0f;
    private static float agentRadius = 1f;  // Ajusta el radio según el tamaño de tus agentes
    private static float avoidDistance = 1.5f;  // Distancia mínima de colisión entre agentes

    // Lista estática de todos los agentes
    private static List<Agent> allAgents = new List<Agent>();

    public void Init(int id, Vector3 startPosition)
    {
        this.id = id;
        oldPos = startPosition;
        moveTo = startPosition;
        transform.position = startPosition;

        // Añadir este agente a la lista de agentes
        allAgents.Add(this);
    }

    public void SetMoveTo(Vector3 newPos)
    {
        oldPos = transform.position;
        moveTo = newPos;
    }

    void Update()
    {
        // Verificar si la posición a la que se moverá el agente está ocupada
        if (!IsPositionOccupied(moveTo))
        {
            transform.position = Vector3.Lerp(transform.position, moveTo, Time.deltaTime * interpolationSpeed);
        }
    }

    private bool IsPositionOccupied(Vector3 targetPosition)
    {
        // Compara la posición de este agente con los demás agentes
        foreach (Agent agent in allAgents)
        {
            // Ignora la comparación consigo mismo
            if (agent.id == this.id) continue;

            // Verificar si el agente ha sido destruido
            if (agent == null) continue;

            // Verifica si el agente está cerca de la posición de destino
            float distance = Vector3.Distance(agent.transform.position, targetPosition);
            if (distance < avoidDistance)
            {
                return true; // La posición está ocupada
            }
        }
        return false; // La posición está libre
    }

}
