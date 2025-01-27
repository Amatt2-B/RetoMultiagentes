using UnityEngine;
using UnityEngine.UIElements;

public class UIController : MonoBehaviour
{
    public VisualElement ui;

    public Button btnStep;

    void Awake () {
        ui = GetComponent<UIDocument>().rootVisualElement;
    }

    private void OnEnable() {
        btnStep = ui.Query<Button>("StepBtn");
        btnStep.clicked += OnStartClicked;
    }

    // Update is called once per frame
    private void OnStartClicked() {
        TCPClient.Instance.Send("step");
    }
}
