using System;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class TCPClient {
    // Implement the server as a singleton
    private static readonly TCPClient _instance = new();
    
    public static TCPClient Instance {
        get {
            return _instance;
        }
    }

    // Server implementation
    private TCPClient() { }

    private Socket socket;

    public async Task<bool> Connect(string host, int port) {
        try {
            IPAddress IPAddr = IPAddress.Parse(host);
            IPEndPoint endPoint = new(IPAddr, port);

            socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

            await Task.Run(() => socket.Connect(endPoint));

            _ = Task.Run(async () => await Recv());

            return true;

        } catch (Exception ex) {
            Debug.LogError($"Connection failed {ex.Message}");
            return false;
        }
    }

    public void Send(string msg) {
        if(socket == null || !socket.Connected) {
            Debug.LogError("Not connected to the server");
            return;
        }

        socket.Send(Encoding.Default.GetBytes(msg));
    }

    public event Action<string> OnRecv;

    private async Task Recv() {
        try {
            while(socket != null && socket.Connected) {
                var lengthBuffer = new byte[4];
                int bytesReceived = await socket.ReceiveAsync(lengthBuffer, SocketFlags.None);
                if(bytesReceived == 0) {
                    Debug.LogWarning("Connection closed by server");
                    break;
                }

                // Read the first 32 bits as an int. Reversed because of endianness 
                int messageLength = BitConverter.ToInt32(lengthBuffer.Reverse().ToArray(), 0);

                var buffer = new byte[messageLength];
                int totalBytesRead = 0;

                // Read multi-part messages
                while(totalBytesRead < messageLength) {
                    int bytesRead = await socket.ReceiveAsync(buffer.AsMemory(totalBytesRead), SocketFlags.None);
                    if(bytesRead == 0) {
                        Debug.LogWarning("Connection closed by server while reading message");
                        return;
                    }
                    totalBytesRead += bytesRead;
                }

                string msg = Encoding.UTF8.GetString(buffer);
                OnRecv?.Invoke(msg);
                
            }
        } catch (Exception ex) {
            Debug.LogError($"Error listening: {ex}");
        }
    }

    public void Disconnect() {
        if(socket != null && socket.Connected) {
            socket.Shutdown(SocketShutdown.Both);
            socket.Close();
            socket = null;
        }

        Debug.Log("Disconnected from server");
    }

}
