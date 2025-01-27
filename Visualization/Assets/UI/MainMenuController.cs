using UnityEngine;
using UnityEngine.UIElements;

public class MainMenuController : MonoBehaviour
{
    public VisualElement ui;

    public Button btnStartServer;
    public TextField fieldHost;
    public IntegerField fieldPort;
    public TextElement connectingLabel;
    public TextElement errorMessageLabel;

    [SerializeField]
    public GameObject uiController;

    private void Awake() {
        ui = GetComponent<UIDocument>().rootVisualElement;
    }

    private void OnEnable() {
        btnStartServer = ui.Query<Button>("ConnectBtn");
        btnStartServer.clicked += OnStartServerClicked;

        fieldHost = ui.Query<TextField>("HostField");
        fieldPort = ui.Query<IntegerField>("PortField");
        connectingLabel = ui.Query<TextElement>("ConnectingLabel");
        errorMessageLabel = ui.Query<TextElement>("ErrorMessage");
    }

    private async void OnStartServerClicked() {
        var client = TCPClient.Instance;

        btnStartServer.AddToClassList("hidden");
        connectingLabel.RemoveFromClassList("hidden");
        bool isConnected = await client.Connect(fieldHost.value, fieldPort.value);
        btnStartServer.RemoveFromClassList("hidden");
        connectingLabel.AddToClassList("hidden");

        if(isConnected) {
            client.Send("start");
            gameObject.SetActive(false);

            // TODO: make the game manager manage this and/or separate the scenes
            uiController.SetActive(true);
        } else {
            errorMessageLabel.text = "Error connecting to server";
            errorMessageLabel.RemoveFromClassList("hidden");
        }
        
    }
}

