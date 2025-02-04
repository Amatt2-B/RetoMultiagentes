using UnityEngine;
using UnityEngine.UIElements;

public class UIController : MonoBehaviour
{
    public VisualElement ui;

    public Button btnStep;
    public Button btnDisonnect;

    [SerializeField]
    private GameObject menuController;

    void Awake () {
        ui = GetComponent<UIDocument>().rootVisualElement;
    }

    private void OnEnable() {
        btnStep = ui.Query<Button>("StepBtn");
        btnStep.clicked += OnStartClicked;
        
        btnDisonnect = ui.Query<Button>("DisconnectBtn");
        btnDisonnect.clicked += OnDisconnectClicked;
    }

    // Update is called once per frame
    private void OnStartClicked() {
        TCPClient.Instance.Send("step");
    }

    private void OnDisconnectClicked() {
        TCPClient.Instance.Disconnect();
        gameObject.SetActive(false);
        menuController.SetActive(true);
    }
}
