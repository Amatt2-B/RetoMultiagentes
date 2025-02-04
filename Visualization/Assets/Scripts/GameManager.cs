using System;
using System.Collections.Generic;
using Messages;
using UnityEngine;

public class GameManager : MonoBehaviour {

    [SerializeField]
    private GameObject carAgentPrefab;

    void Awake() {
        TCPClient.Instance.OnRecv += OnServerMessage;
    }

    private readonly Dictionary<int, Agent> agents = new();

    private bool initialized = false;

    void OnServerMessage(string message) {
        // Debug.Log($"Server says {message}");

        // Get the whole simulation state
        var simstate = JsonUtility.FromJson<SimState>(message);

        // Object instanciation has to be done on the main thread so we use
        // an acton queue to schedule actions on the `Update` method
        Schedule(() => {
            if (!initialized) {
                // TODO: Set init stuff
                initialized = true;
            }

            foreach (var agentData in simstate.agents)
            {
                Vector3 v = new(agentData.pos[0], 0.0f, agentData.pos[1]);

                if (agents.TryGetValue(agentData.id, out Agent agent)) {
                    agent.SetMoveTo(v);
                } else {
                    // TODO: handle different agent types
                    GameObject newAgent = Instantiate(carAgentPrefab, v, Quaternion.identity);
                    agent = newAgent.GetComponent<Agent>();
                    agent.Init(agentData.id, v);
                    agents[agentData.id] = agent;
                }
            }
        });
    }

    void OnDestroy() {
        TCPClient.Instance.Disconnect();
    }

    // Join actions from the async to the main thread
    private static readonly Queue<Action> syncQueue = new();

    void Update() {
        while(syncQueue.Count > 0) {
            var action = syncQueue.Dequeue();
            action?.Invoke();
        }
    }

    public static void Schedule(Action action) {
        if(action == null) return;

        lock (syncQueue) {
            syncQueue.Enqueue(action);
        }
    }

}
