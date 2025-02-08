using UnityEngine;

public class TrafficLight : MonoBehaviour
{
    public int id;
    private new Renderer renderer;

    void Start()
    {
        renderer = GetComponent<Renderer>();
    }

    public void SetState(string state)
    {
        if (state == "red")
            renderer.material.color = Color.red;
        else if (state == "green")
            renderer.material.color = Color.green;
    }
}
