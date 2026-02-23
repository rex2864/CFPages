## VSCode terminal configuration for shortcuts/keybindings

VSCode에 포함되어 있는 terminal에서 shortcuts/keybindings을 사용하고자 할때
VSCode 자체의 shortcuts/keybindings과 겹치는 경우 기본적으로는 terminal이 아니라
VSCode에서 처리가 되도록 되어 있다.

그래서 terminal에서 shortcuts/keybindings이 동작하도록 하려면 아래의 두 설정을 해야한다.

- "Allow Chords" set to false
- "Send Keybindings To Shell" set to true

또는

- "Allow Chords" set to true
- "Commands To Skip Shell"에 원하는 keybindings/shortcuts을 등록


"Allow Chords" 설정의 의미는 입력된 shortcuts/keybindings을 VSCode에서 처리할지 terminal로 보낼지 여부이다.
true(checked)이면 VSCode에서 처리되고, false(unchecked)이면 terminal로 보낸다.

"Send Keybindings To Shell" 설정의 의미는 대부분의 shortcuts/keybindings을 terminal로 보내라는 설정이다.

"Commands To Skip Shell"의 경우 "Add Item"을 통해서 추가된 '명령어ID'에 대해서는 terminal로 보낸다.
기본은 VSCode에서 처리하되, 추가된 '명령어ID'의 경우에는 terminal로 보내도록 한다. 즉, 예외 설정이라고 보면 된다.

---

Date: 2026. 02. 23

Tags: vscode, terminal, chord, shortcuts, keybindings
