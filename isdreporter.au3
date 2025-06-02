#cs
1. Start SWG in windowed mode.
2. Start AutoIt editor/terminal (SciTE) as admin, load isdreporter.au3, press F5 to run the script.
3. Manually get stacks of ISD droids from a crate ingame. I normally use 3 stacks (for chemical, flora, and mineral).
4. Use the ctrl-shift-t hotkey ingame to auto-get a set of survey tools from a crate.
5. Use the ctrl-shift-d hotkey ingame to auto-send a stack of ISD droids.
6. Press ESC ingame to end the script.
7. After the ISD emails arrive, use the /mailsave command ingame.
8. After the ISD emails have been saved, use the /emptymail command ingame (or manually delete the ISD emails).
9. Run isdreporter.py to process the saved mails and submit new spawns to Galaxy Harvester.
#ce

#include <Array.au3>
#include <MsgBoxConstants.au3>

HotKeySet("{ESC}", "_Exit") ; ESC to exit
HotKeySet("+^t", "_GetTools") ; ctrl + shift + t to get survey tools
HotKeySet("+^d", "_SendDroids") ; ctrl + shift + d to send droids

Func _Exit()
    MsgBox(0, "Exit", "isdreporter.au3 has exited." & @CRLF & "Use F5 from SciTE to restart.")
    Exit
EndFunc

Func _IsMouseClicked()
	Local $aResult = DllCall("user32.dll", "int", "GetAsyncKeyState", "int", 0x01)
	Return BitAND($aResult[0], 0x8000) <> 0 ; True or False from the top bits
EndFunc

Func _GetFocus($title, $text, $timeout = 0)
    WinWait($title, $text, $timeout)

    If Not WinActive($title, $text) Then
        WinActivate($title, $text)
    EndIf

    WinWaitActive($title, $text, $timeout)
EndFunc

; Get survey tools from a crate.
Func _GetTools()
	Local $delayms = 750 ; 750ms delay between actions.
	Local $tools = 13 ; You need one survey tool per planet. This should also match the number of uses per ISD stack.
	Local $aCratePos = [0, 0] ; init x,y

	_GetFocus("SwgClient","")

	Send("/echo >> TOOL DE-CRATER {ENTER}")
	Sleep($delayms)
	Send("/echo Press ESC to exit, or click once on a crate of survey tools to begin. {ENTER}")
	Sleep($delayms)

	; Get the position of the crate and do the clicking
	While Not _IsMouseClicked()
		Sleep(10)
	WEnd

	$aCratePos = MouseGetPos()
	Beep(500, 125)
	Sleep($delayms)

	For $i = 1 To $tools
		MouseClick("left", $aCratePos[0], $aCratePos[1], 2)
		Sleep($delayms)
	Next

	Send("/echo Task completed. " & $tools & " survey tools were de-crated.{ENTER}")
EndFunc

; Send ISD droids.
	; The "Choose survey tool" window must be positioned top right corner. Sized about 285 x 175 px, basically as narrow and short as possible at 1080p.
	; The "Choose planet" window must be positioned top right corner. Sized about 285 x 1080 px, basically as narrow and tall as possible at 1080p.
	; A stack of ISD droids can be located at any immovable position onscreen. Stack size should equal planet count.
	; A requisite number of de-crated survey tools must be available in the inventory.

Func _SendDroids()
	Local $delayms = 1000
	Local $aStackPos = [0, 0]; init x,y
	Local $aToolPos = [1700, 110] ; init x,y
	Local $aPlanetPos = [546, 568, 589, 610, 631, 651, 673, 694, 714, 736, 756, 778, 798] ; just y
	Local $aPlanetNames = ["Corellia", "Tatooine", "Lok", "Naboo", "Rori", "Endor", "Talus", "Yavin 4", "Dathomir", "Dantooine", "Taanab", "Chandrila", "Kuat"]

	_GetFocus("SwgClient","")

	Send("/echo >> DROID SENDER {ENTER}")
	Sleep($delayms)
	Send("/echo Press ESC to exit, or click once on a stack of ISD droids to begin. {ENTER}")
	Sleep($delayms)

	; Get the position of the ISD stack and do the clicking
	While Not _IsMouseClicked()
		Sleep(10)
	WEnd

	$aStackPos = MouseGetPos()
	Beep(500, 125)

	For $i = 1 To UBound($aPlanetPos)
		Send("/echo Sending droid to " & $aPlanetNames[$i - 1] & "...{ENTER}")
		Sleep($delayms)

		; double click stackposition (opens toolwindow)
		MouseClick("left", $aStackPos[0], $aStackPos[1], 2)
		Sleep($delayms * 2)

		; click and select toolposition (opens planetwindow)
		MouseClick("left", $aToolPos[0], $aToolPos[1], 1)
		Sleep($delayms)
		Send("{ENTER}")
		Sleep($delayms)

		; click and select planet
		MouseClick("left", $aToolPos[0], $aPlanetPos[$i - 1], 1)
		Sleep($delayms)
		Send("{ENTER}")
		Sleep($delayms)
	Next

	Send("/echo Task completed. " & UBound($aPlanetPos) & " droids were sent. {ENTER}")
EndFunc

; Keep the script running to enable hotkeys
While 1
    Sleep(100)
WEnd