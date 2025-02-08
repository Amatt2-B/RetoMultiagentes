using System;
using System.Collections.Generic;
using Messages;
using UnityEngine;
using UnityEngine.UI;

public class GameManager : MonoBehaviour
{

    [SerializeField]
    GameObject[] carAgentPrefabs; // Array of car prefabs

    [SerializeField]
    GameObject[] pedestrianAgentPrefabs; // Array of pedestrian prefabs

    [SerializeField]
    float stepInterval = 0.5f;

    float time;

    void Awake()
    {
        TCPClient.Instance.OnRecv += OnServerMessage;
    }

    private readonly Dictionary<int, Agent> agents = new();

    private bool initialized = false;

    void OnServerMessage(string message)
    {
        // Debug.Log($"Server says {message}");

        // Get the whole simulation state
        var simstate = JsonUtility.FromJson<SimState>(message);

        // Object instanciation has to be done on the main thread so we use
        // an acton queue to schedule actions on the Update method
        Schedule(() => {
            if (!initialized)
            {
                // TODO: Set init stuff
                initialized = true;
            }

            foreach (var agentData in simstate.agents)
            {
                Vector3 v = new(agentData.pos[0], 0.0f, agentData.pos[1]);

                if (agents.TryGetValue(agentData.id, out Agent agent))
                {
                    agent.SetMoveTo(v);
                }
                else
                {
                    GameObject prefab;
                    if (agentData.type == "car")
                    {
                        // Randomly select a car prefab
                        int randomIndex = UnityEngine.Random.Range(0, carAgentPrefabs.Length);
                        prefab = carAgentPrefabs[randomIndex];
                    }
                    else
                    {
                        // Randomly select a pedestrian prefab
                        int randomIndex = UnityEngine.Random.Range(0, pedestrianAgentPrefabs.Length);
                        prefab = pedestrianAgentPrefabs[randomIndex];
                    }
                    GameObject newAgent = Instantiate(prefab, v, Quaternion.identity);
                    agent = newAgent.GetComponent<Agent>();
                    agent.Init(agentData.id, v);
                    agents[agentData.id] = agent;
                }
            }

            foreach (int id in simstate.deleted)
            {
                if (agents.TryGetValue(id, out Agent agent))
                {
                    agents.Remove(id);
                    Destroy(agent.gameObject);
                }

            }           

        });
    }

    void OnDestroy()
    {
        TCPClient.Instance.Disconnect();
    }

    // Join actions from the async to the main thread
    private static readonly Queue<Action> syncQueue = new();

    void Update()
    {
        while (syncQueue.Count > 0)
        {
            var action = syncQueue.Dequeue();
            action?.Invoke();
        }

        if (initialized)
        {
            time += Time.deltaTime;
            while (time >= stepInterval)
            {
                TCPClient.Instance.Send("step");
                time -= stepInterval;
            }
        }
    }

    public static void Schedule(Action action)
    {
        if (action == null) return;

        lock (syncQueue)
        {
            syncQueue.Enqueue(action);
        }
    }
}