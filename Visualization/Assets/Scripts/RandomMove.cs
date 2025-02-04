using UnityEngine;

public class AutoCarMovement : MonoBehaviour
{
    public float speed = 10f; // Speed of the car
    public Transform[] waypoints; // Array of waypoints for the car to follow
    private int currentWaypointIndex = 0; // Current waypoint index

    void Update()
    {
        if (waypoints.Length == 0)
            return;

        // Move the car towards the current waypoint
        Transform targetWaypoint = waypoints[currentWaypointIndex];
        transform.position = Vector3.MoveTowards(transform.position, targetWaypoint.position, speed * Time.deltaTime);

        // Rotate the car to face the direction of movement
        Vector3 direction = (targetWaypoint.position - transform.position).normalized;
        if (direction != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(direction);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, Time.deltaTime * 5f);
        }

        // Check if the car has reached the current waypoint
        if (Vector3.Distance(transform.position, targetWaypoint.position) < 0.1f)
        {
            currentWaypointIndex = (currentWaypointIndex + 1) % waypoints.Length; // Move to the next waypoint
        }
    }
}