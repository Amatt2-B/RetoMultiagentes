using System.Threading.Tasks;
using UnityEngine;

public class TCPClientController : MonoBehaviour
{
    private void Start()
    {
        // Initiate connection to the server
        ConnectToServer();
    }

    private async void ConnectToServer()
    {
        bool success = await TCPClient.Instance.Connect("127.0.0.1", 42069); // Change IP and port as needed
        if (success)
        {
            Debug.Log("🎉 Successfully connected to the server.");
            // Send a message to the server
            TCPClient.Instance.Send("START");
        }
        else
        {
            Debug.LogError("❌ Failed to connect to the server.");
        }
    }
}
