using UnityEngine;

public class Agent : MonoBehaviour
{
    public int id { get; private set; }
    private Vector3 moveTo;
    private Vector3 oldPos;
    private float interpolationSpeed = 5.0f;

    public void Init(int id, Vector3 startPosition) {
        this.id = id;
        oldPos = startPosition;
        moveTo = startPosition;
        transform.position = startPosition;
    }

    public void SetMoveTo(Vector3 newPos) {
        oldPos = transform.position;
        moveTo = newPos;
    }

    void Update() {
        transform.position = Vector3.Lerp(transform.position, moveTo, Time.deltaTime * interpolationSpeed);
    }
}
