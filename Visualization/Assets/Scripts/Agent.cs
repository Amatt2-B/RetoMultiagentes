using System.Collections.Generic;
using UnityEngine;

public class Agent : MonoBehaviour
{
    public int id { get; private set; }
    private Vector3 moveTo;
    private Vector3 oldPos;
    private float interpolationSpeed = 5.0f;
    private static float agentRadius = 1f;  // Ajusta el radio seg�n el tama�o de tus agentes
    private static float avoidDistance = 1.5f;  // Distancia m�nima de colisi�n entre agentes

    private float rotationSpeed = 10.0f; // Add rotation speed control

    // Lista est�tica de todos los agentes
    private static List<Agent> allAgents = new List<Agent>();

    public void Init(int id, Vector3 startPosition)
    {
        this.id = id;
        oldPos = startPosition;
        moveTo = startPosition;
        transform.position = startPosition;

        // A�adir este agente a la lista de agentes
        allAgents.Add(this);
    }

    public void SetMoveTo(Vector3 newPos)
    {
        oldPos = transform.position;
        moveTo = newPos;
    }

    void Update()
    {
        // Verificar si la posici�n a la que se mover� el agente est� ocupada
        if (!IsPositionOccupied(moveTo))
        {
            // Move position
            transform.position = Vector3.Lerp(transform.position, moveTo, Time.deltaTime * interpolationSpeed);
            
            // Calculate direction
            Vector3 direction = (moveTo - transform.position);
            
            // Only rotate if we're actually moving
            if (direction.magnitude > 0.01f)
            {
                // Calculate target rotation
                Quaternion targetRotation = Quaternion.LookRotation(direction);
                
                // Smoothly rotate
                transform.rotation = Quaternion.Lerp(transform.rotation, targetRotation, Time.deltaTime * rotationSpeed);
            }
        }
    }

    private bool IsPositionOccupied(Vector3 targetPosition)
    {
        // Compara la posici�n de este agente con los dem�s agentes
        foreach (Agent agent in allAgents)
        {
            // Ignora la comparaci�n consigo mismo
            if (agent.id == this.id) continue;

            // Verificar si el agente ha sido destruido
            if (agent == null) continue;

            // Verifica si el agente est� cerca de la posici�n de destino
            float distance = Vector3.Distance(agent.transform.position, targetPosition);
            if (distance < avoidDistance)
            {
                return true; // La posici�n est� ocupada
            }
        }
        return false; // La posici�n est� libre
    }

}
