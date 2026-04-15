;-| Button Remapping |-----------------------------------------------------
[Remap]
x = x
y = y
z = z
a = a
b = b
c = c
s = s
 
;-| Default Values |-------------------------------------------------------
[Defaults]
; Default value for the "time" parameter of a Command. Minimum 1.
command.time = 15
; Default value for the "buffer.time" parameter of a Command. Minimum 1,
; maximum 30.
command.buffer.time = 1
 
;-| Single Button |---------------------------------------------------------
[Command]
name = "a"
command = a
time = 1
buffer.time = 1
 
[Command]
name = "b"
command = b
time = 1
buffer.time = 1
 
[Command]
name = "c"
command = c
time = 1
buffer.time = 1
 
[Command]
name = "x"
command = x
time = 1
buffer.time = 1
 
[Command]
name = "y"
command = y
time = 1
buffer.time = 1
 
[Command]
name = "z"
command = z
time = 1
buffer.time = 1
 
[Command]
name = "start"
command = s
time = 1
buffer.time = 1

;-| Hold Dir |--------------------------------------------------------------
[Command]
name = "holdfwd";Required (do not remove)
command = /$F
time = 1

[Command]
name = "holdback";Required (do not remove)
command = /$B
time = 1

[Command]
name = "holdup" ;Required (do not remove)
command = /$U
time = 1

[Command]
name = "holddown";Required (do not remove)
command = /$D
time = 1

[Command]
name = "holddownfwd"
command = /$DF
time = 1

[Command]
name = "holddownback"
command = /$DB
time = 1

[Command]
name = "holdupback"
command = /$UB
time = 1

[Command]
name = "holdupfwd"
command = /$UF
time = 1
 
;-| Hold Button |-----------------------------------------------------------
[Command]
name = "hold_a"
command = /a
time = 1
buffer.time = 1
 
[Command]
name = "hold_b"
command = /b
time = 1
buffer.time = 1
 
[Command]
name = "hold_c"
command = /c
time = 1
buffer.time = 1
 
[Command]
name = "hold_x"
command = /x
time = 1
buffer.time = 1
 
[Command]
name = "hold_y"
command = /y
time = 1
buffer.time = 1
 
[Command]
name = "hold_z"
command = /z
time = 1
buffer.time = 1
 
[Command]
name = "hold_start"
command = /s
time = 1
buffer.time = 1

;-| Super Motions |--------------------------------------------------------
[Command]
name = "SGS"
command = x, x, F, a
time = 32;24
;buffer.time = 10

[Command]
name = "RSGS"
command = x, x, B, a
time = 32
;buffer.time = 10

[Command]
name = "SGS"
command = x, x, F+a
time = 32
;buffer.time = 10

[Command]
name = "RSGS"
command = x, x, B+a
time = 32
;buffer.time = 10

[Command]
name = "SGS2"
command = x, x, F
time = 24
;buffer.time = 10

[Command]
name = "RSGS2"
command = x, x, B
time = 24
;buffer.time = 10

[Command]
name = "QCFx2"
command = ~D, DF, F, D, DF
time = 21;24

[Command]
name = "QCBx2"
command = ~D, DB, B, D, DB
time = 21;24

;-| Special Motions |--------------------------------------------------------
[Command]
name = "DP"
command = ~F, D, DF
time = 12;15

[Command]
name = "RDP"
command = ~B, D, DB
time = 12;15

[Command]
name = "relf"
command = ~$F
time = 1
buffer.time = 8

[Command]
name = "relb"
command = ~$B
time = 1
buffer.time = 8

[Command]
name = "QCB"
command = ~D, DB, B
time = 15;12

[Command]
name = "QCF"
command = ~D, DF, F
time = 15;12

[Command]
name = "QCBD"
command = ~B, DB, D
time = 15

[Command]
name = "QCFD"
command = ~F, DF, D
time = 15

;-| 2/3 Button Combination |-----------------------------------------------
[Command]
name = "recovery";Required (do not remove)
command = x+y
time = 1

;-| Double Tap |-----------------------------------------------------------
[Command]
name = "FF"     ;Required (do not remove)
command = F, F
time = 10

[Command]
name = "BB"     ;Required (do not remove)
command = B, B
time = 10
 
;-| Dir + Button |---------------------------------------------------------
[Command]
name = "back_x"
command = /$B,x
time = 1

[Command]
name = "back_y"
command = /$B,y
time = 1

[Command]
name = "back_z"
command = /$B,z
time = 1

[Command]
name = "down_x"
command = /$D,x
time = 1

[Command]
name = "down_y"
command = /$D,y
time = 1

[Command]
name = "down_z"
command = /$D,z
time = 1

[Command]
name = "fwd_x"
command = /$F,x
time = 1

[Command]
name = "fwd_y"
command = /$F,y
time = 1

[Command]
name = "fwd_z"
command = /$F,z
time = 1

[Command]
name = "up_x"
command = /$U,x
time = 1

[Command]
name = "up_y"
command = /$U,y
time = 1

[Command]
name = "up_z"
command = /$U,z
time = 1

[Command]
name = "back_a"
command = /$B,a
time = 1

[Command]
name = "back_b"
command = /$B,b
time = 1

[Command]
name = "back_c"
command = /$B,c
time = 1

[Command]
name = "down_a"
command = /$D,a
time = 1

[Command]
name = "down_b"
command = /$D,b
time = 1

[Command]
name = "down_c"
command = /$D,c
time = 1

[Command]
name = "fwd_a"
command = /$F,a
time = 1

[Command]
name = "fwd_b"
command = /$F,b
time = 1

[Command]
name = "fwd_c"
command = /$F,c
time = 1

[Command]
name = "up_a"
command = /$U,a
time = 1

[Command]
name = "up_b"
command = /$U,b
time = 1

[Command]
name = "up_c"
command = /$U,c
time = 1
 
;-| Single Dir |------------------------------------------------------------
[Command]
name = "fwd" ;Required (do not remove)
command = F;$F
time = 1

[Command]
name = "downfwd"
command = DF;$DF
time = 1

[Command]
name = "down" ;Required (do not remove)
command = D;$D
time = 1

[Command]
name = "downback"
command = DB;$DB
time = 1

[Command]
name = "back" ;Required (do not remove)
command = B;$B
time = 1

[Command]
name = "upback"
command = UB;$UB
time = 1

[Command]
name = "up" ;Required (do not remove)
command = U;$U
time = 1

[Command]
name = "upfwd"
command = UF;$UF
time = 1

;---------------------------------------------------------------------------
;Release Direction
[Command]
name = "rlsfwd"
command = ~$F
time = 1

[Command]
name = "rlsback"
command = ~$B
time = 1

[Command]
name = "rlsup"
command = ~$U
time = 1

[Command]
name = "rlsdown"
command = ~$D
time = 1

;--------------------------------------------------------------------------
;Release Button
[Command]
name = "rlsx"
command = ~x
time = 1
buffer.time = 1

[Command]
name = "rlsy"
command = ~y
time = 1
buffer.time = 1

[Command]
name = "rlsz"
command = ~z
time = 1
buffer.time = 1

[Command]
name = "rlsa"
command = ~a
time = 1
buffer.time = 1

[Command]
name = "rlsb"
command = ~b
time = 1
buffer.time = 1

[Command]
name = "rlsc"
command = ~c
time = 1
buffer.time = 1

[Command]
name = "rlss"
command = ~s
time = 1
buffer.time = 1

;---------------------------------------------------------------------------
;Other
[Command]
name = "highjump"
command = $D, $U
time = 15

;---------------------------------------------------------------------------
;It is VERY important to note, that the placement of Changestates, 
;here are HEAVILY important with this buffering system! 
;Even more so than default! I'm adding this notation as a constant, 
;reminder. Don't forget DW to adjust as needed!

;Also ALWAYS and I mean ALWAYS add these two triggers:
;triggerall = !IsHelper(10371) 
;triggerall = numhelper(10371)
;To EVERY Changestate that uses the buffer. You know why!
;Also be sure to adjust the "Tick Fix" on a char by char basis.
[Statedef -1]

[State -1, Tick Fix]
type = CtrlSet
triggerall = RoundState = 2
triggerall = !ctrl
triggerall = movetype!=H
trigger1 = (stateno = 52 || stateno = 101 || stateno = 5120) && !AnimTime
trigger2 = (stateno = [200,299]) && !AnimTime
trigger3 = (stateno = [400,499]) && !AnimTime
trigger4 = (stateno = [700,715]) && !AnimTime
trigger5 = (stateno = [760,762]) && !AnimTime
value = 1

[State -1, CtrlSet For Helpers];special thanks to 20S
type = CtrlSet
trigger1 = IsHelper
value = 0

[State -1, Hit Count For Helpers];special thanks to 20S
type = ParentVarAdd
trigger1 = IsHelper
trigger1 = MoveHit = 1
trigger1 = !HitPauseTime 
trigger1 = !(HitDefAttr = SCA, AT)
var(13) = 1

[State -1, Juggle Count For Helpers];special thanks to 20S
type = ParentVarAdd
trigger1 = IsHelper
trigger1 = MoveHit = 1
trigger1 = !HitPauseTime 
trigger1 = !(HitDefAttr = SCA, AT)
var(15) = 1

[State -1, ProjContact];special thanks to 20S
type = VarSet
trigger1 = IsHelper
trigger1 = MoveContact = 1 && NumTarget
var(18) = 1

[State -1, Root ProjContact];special thanks to 20S
type = ParentVarSet
trigger1 = IsHelper
trigger1 = MoveContact = 1 && NumTarget
var(18) = 1

[State -1, AI Guard Fix]
type = Assertspecial
triggerall = ailevel
trigger1 = stateno != [120,159]
trigger1 = stateno != 5210
flag = noairguard
flag2 = nocrouchguard
flag3 = nostandguard

[State -1, Neo Skullo Dream]
type = ChangeState
value = 3600
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371)
triggerall = helper(10371), var(44)
triggerall = (helper(10371), var(2)) || (helper(10371), var(9))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 3000, power >= 1000)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6)
trigger3 = (StateNo =[200,250]) && StateNo != 222

[State -1, Neo Skullo Dream(Alternate)]
type = ChangeState
value = 3600
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371)
triggerall = helper(10371), var(45)
triggerall = (helper(10371), var(3)) && (helper(10371), var(2))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 3000, power >= 1000)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6)
trigger3 = (StateNo =[200,250]) && StateNo != 222

[State -1, Skullo Dream]
type = ChangeState
value = 3500
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371)
triggerall = helper(10371), var(42)
triggerall = (helper(10371), var(2)) || (helper(10371), var(9))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 3000, power >= 1000)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6)
trigger3 = (StateNo =[200,250]) && StateNo != 222

[State -1, Skullo Dream(Alternate)]
type = ChangeState
value = 3500
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371)
triggerall = helper(10371), var(43)
triggerall = (helper(10371), var(3)) && (helper(10371), var(2))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 3000, power >= 1000)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6)
trigger3 = (StateNo =[200,250]) && StateNo != 222

[State -1, Super Skullo Energy]
type = ChangeState
value = 3400
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371)
triggerall = helper(10371), var(41)
triggerall = (helper(10371), var(3)) && (helper(10371), var(4)) || (helper(10371), var(4)) && (helper(10371), var(5)) || (helper(10371), var(3)) && (helper(10371), var(5)) 
triggerall = RoundState = 2 && StateType != A ;&& !numhelper(3405)
triggerall = ifelse(var(20) <= 0, power >= 2000, power >= 1000)
triggerall = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101]) || var(6) || var(7)
trigger1 = NumHelper(3405) <= 0
trigger2 = NumHelper(3405) <= 1
trigger2 = Helper(3405),StateNo=3205

[State -1, Super Skullo Crusher Max]
type = ChangeState
value = 3050
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(40)
triggerall = (helper(10371), var(0)) && (helper(10371), var(1)) || (helper(10371), var(1)) && (helper(10371), var(2)) || (helper(10371), var(0)) && (helper(10371), var(2))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 2000, power >= 1000)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6) || var(7)

[State -1, Super Skullo Slider Max]
type = ChangeState
value = 3150
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371)
triggerall = helper(10371), var(40)
triggerall = (helper(10371), var(3)) && (helper(10371), var(4)) || (helper(10371), var(4)) && (helper(10371), var(5)) || (helper(10371), var(3)) && (helper(10371), var(5))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 2000, power >= 1000)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6) || var(7)

[State -1, Air Super Skullo Crusher Max]
type = ChangeState
value = 3060
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(40)
triggerall = (helper(10371), var(0)) && (helper(10371), var(1)) || (helper(10371), var(1)) && (helper(10371), var(2)) || (helper(10371), var(0)) && (helper(10371), var(2))
triggerall = RoundState = 2 && StateType = A
triggerall = ifelse(var(20) <= 0, power >= 2000, power >= 1000)
triggerall = var(3)!=[1,2]
trigger1 = ctrl && pos y < -35
trigger2 = var(6) || var(7)

[State -1, Skullo Energy]
type = ChangeState
value = 3300
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(41)
triggerall = (helper(10371), var(3)) || (helper(10371), var(4)) || (helper(10371), var(5)) || (helper(10371), var(10)) || (helper(10371), var(11)) || (helper(10371), var(12))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
triggerall = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101]) || var(6)
trigger1 = NumHelper(3305) <= 0
trigger2 = NumHelper(3305) <= 1
trigger2 = Helper(3305),StateNo=3205

[State -1, Skullo Ball]
type = ChangeState
value = 3200
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(41)
triggerall = (helper(10371), var(0)) || (helper(10371), var(1)) || (helper(10371), var(2)) || (helper(10371), var(7)) || (helper(10371), var(8)) || (helper(10371), var(9))
triggerall = NumHelper(3205) <= 1
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6)

[State -1, Super Skullo Crusher]
type = ChangeState
value = 3000
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(40)
triggerall = (helper(10371), var(0)) || (helper(10371), var(1)) || (helper(10371), var(2)) || (helper(10371), var(7)) || (helper(10371), var(8)) || (helper(10371), var(9))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6)

[State -1, Super Skullo Slider]
type = ChangeState
value = 3100
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(40)
triggerall = (helper(10371), var(3)) || (helper(10371), var(4)) || (helper(10371), var(5)) || (helper(10371), var(10)) || (helper(10371), var(11)) || (helper(10371), var(12))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(6)

[State -1, Air Super Skullo Crusher]
type = ChangeState
value = 3010
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(40)
triggerall = (helper(10371), var(0)) || (helper(10371), var(1)) || (helper(10371), var(2)) || (helper(10371), var(7)) || (helper(10371), var(8)) || (helper(10371), var(9))
triggerall = RoundState = 2 && StateType = A
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
triggerall = var(3)!=[1,2]
trigger1 = ctrl && pos y < -35
trigger2 = var(6)

[State -1, EX Skullo Face Slam]
type = ChangeState
value = 1430
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371)
triggerall = helper(10371), var(23)
triggerall = (helper(10371), var(3)) && (helper(10371), var(4)) || (helper(10371), var(4)) && (helper(10371), var(5)) || (helper(10371), var(3)) && (helper(10371), var(5))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, EX Skullo Head]
type = ChangeState
value = 1230
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(22)
triggerall = (helper(10371), var(0)) && (helper(10371), var(1)) || (helper(10371), var(1)) && (helper(10371), var(2)) || (helper(10371), var(0)) && (helper(10371), var(2))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, EX Skullo Crusher]
type = ChangeState
value = 1030
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(0)) && (helper(10371), var(1)) || (helper(10371), var(1)) && (helper(10371), var(2)) || (helper(10371), var(0)) && (helper(10371), var(2))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, EX Skullo Dive]
type = ChangeState
value = 1330
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(0)) && (helper(10371), var(1)) || (helper(10371), var(1)) && (helper(10371), var(2)) || (helper(10371), var(0)) && (helper(10371), var(2))
triggerall = RoundState = 2 && StateType = A
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
triggerall = var(3)!=[1,2]
trigger1 = ctrl && pos y <= -30
trigger2 = var(5)

[State -1, EX Skullo Slider]
type = ChangeState
value = 1130
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(3)) && (helper(10371), var(4)) || (helper(10371), var(4)) && (helper(10371), var(5)) || (helper(10371), var(3)) && (helper(10371), var(5))
triggerall = RoundState = 2 && StateType != A
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Skullo Face Slam]
type = ChangeState
value = 1400
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(23)
triggerall = (helper(10371), var(3)) || (helper(10371), var(4)) || (helper(10371), var(5)) || (helper(10371), var(10)) || (helper(10371), var(11)) || (helper(10371), var(12))
triggerall = RoundState = 2 && StateType != A
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Strong Skullo Head]
type = ChangeState
value = 1220
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(22)
triggerall = (helper(10371), var(2)) || (helper(10371), var(9))
triggerall = RoundState = 2 && StateType != A
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Medium Skullo Head]
type = ChangeState
value = 1210
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(22)
triggerall = (helper(10371), var(1)) || (helper(10371), var(8))
triggerall = RoundState = 2 && StateType != A
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Skullo Head]
type = ChangeState
value = 1200
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(22)
triggerall = (helper(10371), var(0)) || (helper(10371), var(7))
triggerall = RoundState = 2 && StateType != A
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Alpha Counter(Kick)]
type = ChangeState
value = 750
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(20)
triggerall = (helper(10371), var(3)) || (helper(10371), var(4)) || (helper(10371), var(5)) || (helper(10371), var(10)) || (helper(10371), var(11)) || (helper(10371), var(12))
trigger1 = StateNo = 150 || StateNo = 152
trigger1 = RoundState = 2 && StateType != A
trigger1 = power >= 1000 && !var(20)

[State -1, Alpha Counter(Punch)]
type = ChangeState
value = 750
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(20)
triggerall = (helper(10371), var(0)) || (helper(10371), var(1)) || (helper(10371), var(2)) || (helper(10371), var(7)) || (helper(10371), var(8)) || (helper(10371), var(9))
trigger1 = StateNo = 150 || StateNo = 152
trigger1 = RoundState = 2 && StateType != A
trigger1 = power >= 1000 && !var(20)

[State -1, Skullo Crusher]
type = ChangeState
value = 1000
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(0)) || (helper(10371), var(1)) || (helper(10371), var(2)) || (helper(10371), var(7)) || (helper(10371), var(8)) || (helper(10371), var(9))
triggerall = RoundState = 2 && StateType != A
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Strong Skullo Dive]
type = ChangeState
value = 1320
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(2)) || (helper(10371), var(9)) 
triggerall = RoundState = 2 && StateType = A
triggerall = var(3)!=[1,2]
trigger1= ctrl && pos y <= -30
trigger2 = var(5)

[State -1, Medium Skullo Dive]
type = ChangeState
value = 1310
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(1)) || (helper(10371), var(8)) 
triggerall = RoundState = 2 && StateType = A
triggerall = var(3)!=[1,2]
trigger1= ctrl && pos y <= -30
trigger2 = var(5)

[State -1, Skullo Dive]
type = ChangeState
value = 1300
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(0)) || (helper(10371), var(7)) 
triggerall = RoundState = 2 && StateType = A
triggerall = var(3)!=[1,2]
trigger1= ctrl && pos y <= -30
trigger2 = var(5)

[State -1, Strong Skullo Slider]
type = ChangeState
value = 1120
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(5)) || (helper(10371), var(12))
triggerall = RoundState = 2 && StateType != A
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Medium Skullo Slider]
type = ChangeState
value = 1110
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(4)) || (helper(10371), var(11))
triggerall = RoundState = 2 && StateType != A
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Skullo Slider]
type = ChangeState
value = 1100
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(21)
triggerall = (helper(10371), var(3)) || (helper(10371), var(10))
triggerall = RoundState = 2 && StateType != A
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = var(5)

[State -1, Counter Movement]
type = ChangeState
value = 740
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(14);LP+LK detection
triggerall = (helper(10371),command = "holdfwd") || (helper(10371),command = "holdback")
trigger1 = StateNo = 150 || StateNo = 152
trigger1 = RoundState = 2 && StateType != A
trigger1 = power >= 1000 && !var(20)

[State -1, Air Throw]
type = ChangeState
value = 900
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = (helper(10371), var(0)) && (helper(10371), var(1)) || (helper(10371), var(1)) && (helper(10371), var(2)) || (helper(10371), var(0)) && (helper(10371), var(2))
trigger1 = (helper(10371),command = "holdfwd")|| (helper(10371),command = "holdback")
trigger1 = RoundState = 2 && StateType = A
trigger1 = ctrl && pos y <= -30
trigger1 = statetype != S

[State -1, Throw]
type = ChangeState
value = 800
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = (helper(10371), var(0)) && (helper(10371), var(1)) || (helper(10371), var(1)) && (helper(10371), var(2)) || (helper(10371), var(0)) && (helper(10371), var(2))
trigger1 = (helper(10371),command = "holdfwd")|| (helper(10371),command = "holdback")
trigger1 = RoundState = 2 && StateType = S
trigger1 = ctrl

[State -1, Roll Forward]
type = ChangeState
value = 710
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(14) ;LP+LK detection
triggerall = RoundState = 2 && StateType != A
trigger1 = (ctrl || (StateNo = [100,101])) && command = "holdfwd"

[State -1, Roll Back]
type = ChangeState
value = 715
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(14) ;LP+LK detection
triggerall = RoundState = 2 && StateType != A
trigger1 = (ctrl || (StateNo = [100,101])) && command = "holdback"

[State -1, Power Charge]
type = ChangeState
value = 730
triggerall = !ailevel
trigger1 = command = "hold_b" && command = "hold_y"
trigger1 = RoundState = 2 && StateType != A
trigger1 = power < const(data.power) && power < PowerMax && !var(20)
trigger1 = ctrl || (StateNo = [100,101])
;^I'm gonna have to adapt this to the buffering system(maybe?) 
;I think it's good... I'll keep this as a reminder still though

[State -1, MAX Mode]
type = ChangeState
value = 770
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(16) ;HP+HK detection
triggerall = RoundState = 2 && StateType != A
triggerall = var(20) <= 0 && Power >= 1000
trigger1 = ctrl || (Stateno = [100,101])

[State -1, Dodge]
type = ChangeState
value = 700
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(14) ;LP+LK detection
triggerall = RoundState = 2 && StateType != A
trigger1 = (ctrl || (StateNo = [100,101]))

[State -1, Dangerous Heel]
type = Changestate
value = 241
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(4) ; The buffered version of MK
triggerall = (helper(10371),command != "holddown")
triggerall = command = "holdfwd"
triggerall = statetype != A
trigger1 = statetype = S
trigger1 = ctrl || (stateno=[100,101])

[State -1, Step-In Upper]
type = Changestate
value = 211
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(1) ; The buffered version of MP
triggerall = (helper(10371),command != "holddown")
triggerall = command = "holdfwd"
triggerall = statetype != A
trigger1 = statetype = S
trigger1 = ctrl || (stateno=[100,101])

[State -1, Step-In Upper Combo'd]
type = Changestate
value = 212
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this!
triggerall = numhelper(10371)
triggerall = helper(10371), var(1) ; The buffered version of MP
triggerall = (helper(10371),command != "holddown")
triggerall = command = "holdfwd"
triggerall = statetype != A
trigger1 = statetype = S
trigger1 = ctrl || (stateno=[100,101])
trigger2 = var(4)

[State -1, Run Fwd]
type = ChangeState
value = 100
triggerall = !ailevel
trigger1 = command = "FF"
trigger1 = statetype = S
trigger1 = ctrl

[State -1, Run Back]
type = ChangeState
value = 105
triggerall = !ailevel
trigger1 = command = "BB"
trigger1 = statetype = S
trigger1 = ctrl

;|Normal Commands|--------------------------------------------------------
[State -1, Stand Light Punch]
type = ChangeState
value = 200
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(0) ; The buffered version of LP
triggerall = (helper(10371),command != "holddown")
;^Be sure to include the dir buffer check if needed DW!
trigger1 = statetype != A
trigger1= ctrl || (stateno=[100,101])
trigger2= (StateNo = 200 || StateNo = 400 || StateNo = 430) && Time >=5

[State -1, Stand Medium Punch]
type = ChangeState
value = 210 
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(1) ; The buffered version of MP
triggerall = (helper(10371),command != "holddown")
triggerall = command != "holdfwd"  
triggerall = StateType != A
trigger1 = ctrl || (StateNo = [100,101])

[State -1, Stand Strong Punch]
type = ChangeState
value = 220 
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(2) ; The buffered version of HP
triggerall = (helper(10371),command != "holddown") 
triggerall = StateType != A
trigger1 = ctrl || (StateNo = [100,101])

[State -1, Stand Light Kick]
type = ChangeState
value = 230
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(3) ; The buffered version of LK
triggerall = (helper(10371),command != "holddown")
trigger1 = statetype != A
trigger1= ctrl || (stateno=[100,101])

[State -1, Stand Medium Kick]
type = ChangeState
value = 240
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(4) ; The buffered version of MK
triggerall = (helper(10371),command != "holddown")
triggerall = command != "holdfwd"
trigger1 = statetype != A
trigger1= ctrl || (stateno=[100,101])

[State -1, Standing Strong Kick]
type = ChangeState
value = 250
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(5) ; The buffered version of HK
triggerall = (helper(10371),command != "holddown")
trigger1 = statetype != A
trigger1= ctrl || (stateno=[100,101])

[State -1, Crouching Light Punch]
type = ChangeState
value = 400
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(0) ; The buffered version of LP
triggerall = (helper(10371),command = "holddown")
triggerAll = StateType != A
trigger1 = ctrl || (StateNo = [100,101])
trigger2= (StateNo = 200 || StateNo = 400 || StateNo = 430) && Time >=5

[State -1, Crouching Medium Punch]
type = ChangeState
value = 410
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(1) ; The buffered version of MP
triggerall = (helper(10371),command = "holddown")
triggerAll = StateType != A
trigger1 = ctrl || (StateNo = [100,101])

[State -1, Crouching Strong Punch]
type = ChangeState
value = 420
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(2) ; The buffered version of HP
triggerall = (helper(10371),command = "holddown")
triggerAll = StateType != A
trigger1 = ctrl || (StateNo = [100,101])

[State -1, Crouching Light Kick]
type = ChangeState
value = 430
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(3) ; The buffered version of LK
triggerall = (helper(10371),command = "holddown")
triggerAll = StateType != A
trigger1 = ctrl || (StateNo = [100,101])
trigger2= (StateNo = 200 || StateNo = 400 || StateNo = 430) && Time >=5

[State -1, Crouching Medium Kick]
type = ChangeState
value = 440
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(4) ; The buffered version of MK
triggerall = (helper(10371),command = "holddown")
triggerAll = StateType != A
trigger1 = ctrl || (StateNo = [100,101])
trigger2 = StateNo = 410 && MoveContact=[2,4]

[State -1, Crouching Strong Kick]
type = ChangeState
value = 450
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(5) ; The buffered version of HK
triggerall = (helper(10371),command = "holddown")
triggerAll = StateType != A
trigger1 = ctrl || (StateNo = [100,101])

[State -1, Jump Light Punch]
type = ChangeState
value = 600
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(0) ; The buffered version of LP
trigger1 = statetype = A
trigger1 = ctrl

[State -1, Jump Med Punch]
type = ChangeState
value = 610
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(1) ; The buffered version of MP
trigger1 = statetype = A
trigger1 = ctrl

[State -1, Jump Strong Punch]
type = ChangeState
value = 620
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(2) ; The buffered version of HP
trigger1 = statetype = A
trigger1 = ctrl

[State -1, Jump Light Kick]
type = ChangeState
value = 630
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(3) ; The buffered version of LK
trigger1 = statetype = A
trigger1 = ctrl

[State -1, Jump Med Kick]
type = ChangeState
value = 640
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(4) ; The buffered version of MK
trigger1 = statetype = A
trigger1 = ctrl

[State -1, Jump Strong Kick]
type = ChangeState
value = 650
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(5) ; The buffered version of HK
trigger1 = statetype = A
trigger1 = ctrl

[State -1, Taunt]
type = ChangeState
value = 195
triggerall = !ailevel
triggerall = !IsHelper(10371) ;Always add this as well!
triggerall = numhelper(10371) ;Prevent debug flood.
triggerall = helper(10371), var(6) ; The buffered version of Start
triggerall = StateType != A
triggerall = StateNo != [200,699]
trigger1 = ctrl || (StateNo = [100,101])
trigger2 = var(5)

;---------------------------------------------------------------------------
;AI System Moves
;---------------------------------------------------------------------------
[state -1, AI 20 Walk]
type = changestate
value = 20
triggerall = ailevel
triggerall = roundstate = 2
triggerall = numenemy
triggerall = statetype = S
triggerall = p2stateno != 5120 && p2stateno != 5201 || enemynear,ctrl
;condition
trigger1 = ctrl
trigger1 = p2bodydist x = [cond(numtarget, -const240p(8), const240p(32)), const240p(160)]
trigger1 = p2movetype != A
trigger1 = !(enemynear, numproj)
trigger1 = stateno != [20, 119]
trigger1 = prevstateno != [20, 119]
trigger1 = gametime % floor(42 - (ailevel * 4.0)) = [0, ailevel]

[State -1, AI 5210 Fall Recovery]
type = changestate
value = 5210
trigger1 = AIlevel && numenemy
trigger1 = roundstate = 2 && alive
trigger1 = stateno = 5050 && canrecover
trigger1 = Vel Y > Const(movement.air.gethit.airrecover.threshold)
trigger1 = random < (25 * (AIlevel ** 2.0 / 64.0))

[State -1, AI 5200 Fall Recovery]
type = changestate
value = 5200
trigger1 = AIlevel && numenemy
trigger1 = roundstate = 2 && alive
trigger1 = stateno = 5050 && canrecover
trigger1 = Vel Y > 0 && Pos Y >= Const(movement.air.gethit.groundrecover.ground.threshold)
trigger1 = random < (100 * (AIlevel ** 2.0 / 64.0))

[State -1, AI 40 Jump]
type = changestate
value = 40
triggerall = ailevel && numenemy
triggerall = roundstate = 2 && statetype != A
; condition
trigger1 = ctrl || (stateno = [100, 101]) || (stateno = [120, 131])
trigger1 = enemynear, movetype = A && p2bodydist x < 160 && enemynear, hitdefattr = SC, AT
trigger1 = random < (250 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = ctrl || (stateno = [100, 101])
trigger2 = backedgebodydist <= const240p(32)
trigger2 = p2statetype = L
trigger2 = p2bodydist x < const240p(128)
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = ctrl || (stateno = [100, 101]) || (stateno = [120, 131])
trigger3 = p2movetype = A
trigger3 = p2statetype != A
trigger3 = (p2stateno = [1000, 1999]) || (enemynear, hitdefattr = SCA, SA, SP, ST)
trigger3 = enemynear, animtime < -32
trigger3 = p2bodydist x > const240p(90) || frontedgebodydist < const240p(60) || backedgebodydist < const240p(32)
trigger3 = (random < (25 * (ailevel ** 2.0 / 64.0))) || (enemynear, time = [7, 12])
trigger3 = (random < (25 * (ailevel ** 2.0 / 64.0))) || p2bodydist x > const240p(120)
trigger3 = random < (200 * (ailevel ** 2.0 / 64.0))

[State -1, AI 120 Guard]
type = changestate
value = 120
triggerall = ailevel && cond(numhelper(4000), helper(4000),var(58), 1)
triggerall = roundstate = 2
triggerall = numenemy
triggerall = inguarddist
; condition
trigger1 = ctrl && (stateno != [120, 155])
trigger1 = !var(26) && p2bodydist x >= const(size.ground.front) * 2.5
trigger1 = !(enemynear, hitdefattr = SCA, AT) && (enemynear, time < 120)
trigger1 = statetype != A || p2statetype = A
trigger1 = ifelse(statetype = A, ((var(3) != [1, 2]) || stateno = 5210), 1)
trigger1 = random < (cond((enemynear, hitdefattr = SCA, NA), 100, cond((enemynear, hitdefattr = SCA, SA), 333, 1000)) * (ailevel ** 2.0 / 64.0))

[State -1, AI 730 Power Charge]
type = changestate
value = 730
triggerall = ailevel && numenemy
trigger1 = roundstate = 2 && statetype != A
; condition
trigger1 = ctrl && power < const(data.power) && power < powerMax && prevstateno != 5120 && !var(20)
trigger1 = !inguarddist && p2bodydist x >= 160
trigger1 = random < (cond(power < 1000 && p2statetype = L, 250, 100 * (ailevel ** 2.0 / 64.0)))

[State -1, AI 105 Dash Backward]
type = changestate
value = 105
triggerall = ailevel && numenemy
triggerall = statetype = S
triggerall = ctrl && !inguarddist
; condition
trigger1 = backedgebodydist > const240p(80) && p2statetype = L && p2bodydist x = [-8, 32]
trigger1 = random < 200 * (ailevel ** 2.0 / 64.0)

[State -1, AI 750 Zero Counter]
type = changestate
value = 750
trigger1 = AIlevel && numenemy
trigger1 = stateno = 150 || stateno = 152
trigger1 = roundstate = 2 && statetype != A
trigger1 = power >= 1000 && !var(20)
trigger1 = (p2bodydist x = [0, 50]) && (life < 0.5 * lifemax)
trigger1 = random < (3 ** (floor(power / 750.0)))

[State -1, AI 740 Counter Movement]
type = ChangeState
value = 740
trigger1 = ailevel && numenemy
trigger1 = stateno = 150 || stateno = 152
trigger1 = roundstate = 2 && statetype != A
trigger1 = power >= 1000 && !var(20)
; condition
trigger1 = (p2bodydist x = [0,50]) && (life < 0.5 * lifemax)
trigger1 = enemynear, animtime = [-45,-30]
trigger1 = random < (power / 10.0)
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))

[State -1, AI 715 Roll Back]
type = ChangeState
value = 715
trigger1 = ailevel && numenemy
trigger1 = roundstate = 2 && statetype != A
trigger1 = frontedgedist < backedgedist
; condition
triggerall = enemynear,hitdefattr != SC,AT
; condition
trigger1 = (ctrl || (stateno = [100, 101]) || (stateno = [120, 131]))
trigger1 = enemynear, movetype = A
trigger1 = inguarddist
trigger1 = (enemynear, stateno != [200, 699]) || (enemynear, animtime = [-28, -42])
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))

[State -1, AI 710 Roll Forward]
type = changestate
value = 710
triggerall = ailevel && numenemy
triggerall = roundstate = 2 && statetype != A
triggerall = ctrl || (stateno = [100, 101]) || (stateno = [120, 131])
; condition
triggerall = enemynear,hitdefattr != SC,AT
; condition
trigger1 = (p2bodydist X = [56,80]) || (p2bodydist X = [108,160]) || backedgebodydist <= const240p(32)
trigger1 = !enemynear, ctrl && p2movetype != H
trigger1 = enemynear, animtime = [-45,-30]
trigger1 = random < (75 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = ctrl || (stateno = [101, 102]) || (stateno = [120,131])
trigger2 = p2statetype = A
trigger2 = p2movetype != H
trigger2 = enemynear, vel x > 0
trigger2 = enemynear, vel y < const240p(1)
trigger2 = p2dist x < const240p(16)
trigger2 = random < (50 * (ailevel ** 2.0 / 64.0))

[State -1, AI 700 Dodge]
type = changestate
value = 700
trigger1 = AIlevel && numenemy
trigger1 = roundstate = 2 && statetype != A
; condition
triggerall = enemynear,hitdefattr != SC,AT
; condition
trigger1 = ctrl || (stateno = [100, 101]) || ((stateno = [120, 131]) && random < (25 * (ailevel ** 2 / 64.0)))
trigger1 = inguarddist
trigger1 = p2bodydist x > 32 || backedgebodydist <= const240p(32)
trigger1 = p2statetype != A
trigger1 = (enemynear, hitdefattr != SCA, NA)  || enemynear, animtime < -40
trigger1 = random < ((lifemax-life)/(lifemax/const(data.life)))/(13.0 - ailevel)

[State -1, AI 770 MAX Mode]
type = ChangeState
value = 770
triggerall = ailevel && numenemy
triggerall = RoundState = 2 && StateType != A
triggerall = var(20) <= 0 && Power >= 1000
triggerall = enemynear, life > (enemynear, lifemax / 4.0)
triggerall = life > (lifemax / 5.0)
triggerall = power < 3000
triggerall = ctrl || (stateno = [100,101])
; condition
trigger1 = p2bodydist x >= 160
trigger1 = enemynear, movetype != A
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = enemynear, stateno = 5110
trigger2 = enemynear, time < enemynear, const(data.liedown.time) - 20
trigger2 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = p2statetype = L
trigger3 = p2bodydist x >= 160
trigger3 = random < (50 * (ailevel ** 2.0 / 64.0))

[State -1, AI 800 Throw]
type = changestate
value = 800
triggerall = AIlevel && numenemy
triggerall = roundstate = 2 && statetype = S
triggerall = !enemynear, ctrl && p2statetype != L && p2movetype != H
;Clsn1: 1
;  Clsn1[0] = 2, -35, 38, 0
triggerall = (p2bodydist x = [-8, 38 - const(size.ground.front)]) && (p2dist y = [-72, 8])
; condition
trigger1 = ctrl
trigger1 = random < (125 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = ctrl && (p2stateno = [120,140])
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 900 Air Throw]
type = changestate
value = 900
triggerall = AIlevel && numenemy
triggerall = roundstate = 2 && statetype = A
triggerall = ctrl && pos y <= -30
trigger1 = p2statetype = A
trigger1 = p2movetype != H
;Clsn2Default: 1
;  Clsn2[0] = -21, -106, 27, -31
;condition
trigger1 = p2statetype = A
trigger1 = p2movetype != H
trigger1 = p2bodydist x = [0, 27]
trigger1 = p2bodydist y = [-50, 50]
trigger1 = random < (250 * (AIlevel ** 2.0 / 64.0))
;condition
trigger2 = p2statetype = A
trigger2 = p2movetype = H || (p2stateno = [120, 155])
trigger2 = p2bodydist x = [0, 50]
trigger2 = p2bodydist y = [-50, 50]
trigger2 = random < (500 * (AIlevel ** 2.0 / 64.0))

;=========================================================================
; AI Normal Commands -----------------------------------------------------
;=========================================================================
[State -1, AI 410 Crouching Medium Punch]
type = ChangeState
value = 410
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = p2statetype != A
; startup = 7
;Clsn1: 1
;  Clsn1[0] = 39, -68, 84, -54
triggerall = p2bodydist x = [-const240p(8), (84 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-68 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (125 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 7))
;condition
trigger2 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger2 = enemynear, gethitvar(hittime) >= 7
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 440 Crouching Medium Kick]
type = ChangeState
value = 440
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; startup = 8
;Clsn1: 1
;  Clsn1[0] = 45, -27, 105, -9
triggerall = p2bodydist x = [-const240p(8), (105 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-27 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = p2statetype != A
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (125 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 8))
; condition
trigger2 = StateNo = 410 && MoveContact && AnimElemTime(4) < 0
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))
;condition
trigger3 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger3 = enemynear, gethitvar(hittime) >= 8
trigger3 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 420 Crouching Strong Punch]
type = ChangeState
value = 420
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
; startup = 8
;Clsn1: 1
;  Clsn1[0] = 27, -75, 63, -40
; startup = 10
;Clsn1: 1
;  Clsn1[0] = 30, -133, 50, -66
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = p2bodydist x >= ((-63 + (10 * enemynear, vel x * (enemynear, statetype = A))) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2bodydist x <= ((63 + (10 * enemynear, vel x * (enemynear, statetype = A))) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [(-133 - (((enemynear, vel y) + (10 * enemynear, const(movement.yaccel))) * (p2statetype = A))) * const(size.yscale), const240p(8)]
trigger1 = enemynear, vel y > -1
trigger1 = random < (cond(p2statetype = A, 250, 50) * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 8))
;condition
trigger2 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger2 = enemynear, gethitvar(hittime) >= 8
trigger2 = p2bodydist x = [-const240p(8), (50 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [(-75 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 200 Stand Light Punch]
type = ChangeState
value = 200
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; startup = 4
;Clsn1: 1
;  Clsn1[0] = 21, -90, 62, -74
triggerall = p2bodydist x = [-const240p(8), (62 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-90 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = p2statetype != C
; condition
trigger1 = StateType != A
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (100 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 4))
; condition
trigger2= (StateNo = 200 || StateNo = 400 || StateNo = 430) && Time >=5
trigger2 = (random < (25 * (ailevel ** 2.0 / 64.0))) || movecontact
trigger2 = random < (100 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger3 = enemynear, gethitvar(hittime) >= 4
trigger3 = p2bodydist x = [-const240p(8), (62 - const(size.ground.front)) * const(size.xscale)]
trigger3 = p2dist y = [(-90 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger3 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 430 Crouching Light Kick]
type = ChangeState
value = 430
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; startup = 5
;Clsn1: 1
;  Clsn1[0] = 48, -16, 106, 0
triggerall = p2bodydist x = [-const240p(8), (106 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-16 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = p2statetype != A
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (125 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 5))
; condition
trigger2 = ctrl || (StateNo = [100,101])
trigger2 = (StateNo = 200 || StateNo = 400 || StateNo = 430) && Time > 5
trigger2 = random < (75 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger3 = enemynear, gethitvar(hittime) >= 5
trigger3 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 210 Stand Medium Punch]
type = ChangeState
value = 210 
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = p2statetype = S

; startup = 7
;Clsn1: 1
;  Clsn1[0] = 29, -85, 75, -67
triggerall = p2bodydist x = [-const240p(8), (75 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-85 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = p2statetype != C
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (100 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 7))
; condition
trigger2 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger2 = enemynear, gethitvar(hittime) >= 7
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 400 Crouching Light Punch]
type = ChangeState
value = 400
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; startup = 4
;Clsn1: 1
;  Clsn1[0] = 32, -67, 80, -52
triggerall = p2bodydist x = [-const240p(8), (80 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-67 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = (enemynear, const(size.head.pos.y) <= -40)
triggerall = p2statetype != A
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (100 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 4))
; condition
trigger2= (StateNo = 200 || StateNo = 400 || StateNo = 430) && Time >=5
trigger2 = random < (100 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger3 = enemynear, gethitvar(hittime) >= 4
trigger3 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 450 Crouching Strong Kick]
type = ChangeState
value = 450
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = (p2statetype = S || (p2statetype = C && p2movetype = H))
; startup = 10
;Clsn1: 1
;  Clsn1[0] = 30, -20, 103, 0
triggerall = p2bodydist x = [-const240p(8), (103 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-20 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = p2statetype != A
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = !enemynear, ctrl && (p2stateno != [120,155])
trigger1 = (p2bodydist x > (40 - const(size.ground.front)) * const(size.xscale)) || numtarget
trigger1 = random < (75 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 10))
; condition
trigger2 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger2 = enemynear, gethitvar(hittime) >= 10
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 240 Stand Medium Kick]
type = ChangeState
value = 240
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = p2statetype != C
; startup = 8
;Clsn1: 1
;  Clsn1[0] = 31, -71, 89, -52
triggerall = p2bodydist x = [-const240p(8), (89 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-71 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = (enemynear, const(size.head.pos.y) <= -40)
triggerall = p2statetype = S
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (75 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 8))
; condition
trigger2 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger2 = enemynear, gethitvar(hittime) >= 8
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 220 Stand Strong Punch]
type = ChangeState
value = 220 
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = p2statetype = S
; startup = 10
;Clsn1: 1
;  Clsn1[0] = 29, -88, 79, -70
triggerall = p2bodydist x = [-const240p(8), (79 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-88 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = StateType != A
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = p2statetype != C
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (75 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 10))
; condition
trigger2 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger2 = enemynear, gethitvar(hittime) >= 7
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 230 Stand Light Kick]
type = ChangeState
value = 230
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; startup = 7
;Clsn1: 1
;  Clsn1[0] = -3, -98, 55, -74
triggerall = p2bodydist x = [-const240p(8), (55 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-98 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 7))
; condition
trigger2 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger2 = enemynear, gethitvar(hittime) >= 7
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 250 Standing Strong Kick]
type = ChangeState
value = 250
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; startup = 12
;Clsn1: 1
;  Clsn1[0] = 29, -77, 105, -55
triggerall = p2bodydist x = [-const240p(8), (105 - const(size.ground.front)) * const(size.xscale)]
triggerall = p2dist y = [(-77 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = p2statetype = S
; condition
trigger1 = ctrl || (stateno=[100,101])
trigger1 = (p2bodydist x > (50 - const(size.ground.front)) * const(size.xscale)) || numtarget
trigger1 = random < (75 * (ailevel ** 2.0 / 64.0)) + (ailevel * 48.0 * (enemynear, gethitvar(hittime) >= 12))
; condition
trigger2 = (((stateno = [200, 499]) && !animtime && movehit) || (ctrl && (enemynear, gethitvar(damage))))
trigger2 = enemynear, gethitvar(hittime) >= 12
trigger2 = random < (250 * (ailevel ** 2.0 / 64.0))

;---------------------------------------------------------------------------
;AI Command Moves
;---------------------------------------------------------------------------
[State -1, AI 211 Step-In Upper]
type = Changestate
value = 211
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
;startup = 12
;Clsn1: 1
;  Clsn1[0] = 31, -93, 68, -42
trigger1 = statetype = S
trigger1 = ctrl || (stateno=[100,101])
trigger1 = p2bodydist x = [-const240p(8), (68 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-93 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))

[State -1, AI 241 Dangerous Heel]
type = Changestate
value = 241
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = p2statetype != A
;startup = 15
;Clsn1: 1
;  Clsn1[0] = 11, -77, 71, -53
trigger1 = statetype = S
trigger1 = ctrl || (stateno=[100,101])
trigger1 = p2bodydist x = [-const240p(8), (71 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-77 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = random < (cond(p2statetype = C, 50, 25) * (AIlevel ** 2.0 / 64.0))

[State -1, AI 212 Step-In Upper Comboed]
type = Changestate
value = 212
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = p2statetype != A
;
trigger1 = statetype = S
trigger1 = ctrl || (stateno=[100,101])
trigger1 = p2bodydist x = [-const240p(8), (68 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-93 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))
;
trigger2 = var(4)
trigger2 = p2bodydist x = [-const240p(8), (48 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [(-93 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 12
trigger2 = random < (150 * (ailevel ** 2.0 / 64.0))

;============================================================================
; AI Jumping Moves ----------------------------------------------------------
;============================================================================
[State -1, AI 650 Jump Strong Kick]
type = ChangeState
value = 650
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype = A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
; startup = 9
;Clsn1: 1
;  Clsn1[0] = -18, -71, 78, -43
triggerall = (vel y >= 0.5 && p2dist y >= -72) || p2statetype = A
; condition
trigger1 = statetype = A
trigger1 = ctrl
trigger1 = p2bodydist x >= (-18 - const(size.ground.front)) * const(size.xscale)
trigger1 = p2bodydist x <= (78 + (9 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [(-71 - 16) * const(size.yscale), (-46 + 72 + (32 * vel y * (vel y > 0))) * const(size.yscale)]
trigger1 = random < (150 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = statetype = A
trigger2 = ctrl
trigger2 = p2bodydist x >= (-18 - const(size.ground.front)) * const(size.xscale)
trigger2 = p2bodydist x <= (78 + (9 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)
trigger2 = p2dist y = [(-71 - 16) * const(size.yscale), (-46 + 72 + 32 * (vel y > 2.0)) * const(size.yscale)]
trigger2 = p2statetype != A && vel y >= 0.5
trigger2 = random < 300 * (ailevel ** 2.0 / 64.0)

[State -1, AI 640 Jump Medium Kick]
type = ChangeState
value = 640
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype = A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
; startup = 6
;Clsn1: 1
;  Clsn1[0] = 27, -56, 66, -35
triggerall = (vel y >= 0.5 && p2dist y >= -50) || p2statetype = A
;
trigger1 = statetype = A
trigger1 = ctrl
trigger1 = p2bodydist x = [-const240p(8), (66 + (6 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-56 - 16) * const(size.yscale), (-35 + 72 + (32 * vel y * (vel y > 0))) * const(size.yscale)]
trigger1 = random < (150 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = statetype = A
trigger2 = ctrl
trigger2 = p2bodydist x = [-const240p(8), (66 + (6 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [(-56 - 16) * const(size.yscale), (-35 + 72 + 32 * (vel y > 2.0)) * const(size.yscale)]
trigger2 = p2statetype != A && vel y >= 0.5
trigger2 = random < 300 * (ailevel ** 2.0 / 64.0)

[State -1, AI 610 Jump Medium Punch]
type = ChangeState
value = 610
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype = A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
; startup = 9
;Clsn1: 1
;  Clsn1[0] = 17, -63, 38, -30
triggerall = (vel y >= 0.5 && p2dist y >= -72) || p2statetype = A
;
trigger1 = statetype = A
trigger1 = ctrl
trigger1 = p2bodydist x = [-const240p(8), (38 + (9 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-63 - 16) * const(size.yscale), (-30 + 72 + (32 * vel y * (vel y > 0))) * const(size.yscale)]
trigger1 = random < (150 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = statetype = A
trigger2 = ctrl
trigger2 = p2bodydist x = [-const240p(8), (38 + (5 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [(-63 - 16) * const(size.yscale), (-30 + 72 + 32 * (vel y > 2.0)) * const(size.yscale)]
trigger2 = p2statetype != A && vel y >= 0.5
trigger2 = random < 300 * (ailevel ** 2.0 / 64.0)

[State -1, AI 620 Jump Strong Punch]
type = ChangeState
value = 620
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype = A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
; startup = 10
;Clsn1: 1
;  Clsn1[0] = 19, -72, 38, -28
triggerall = (vel y >= 0.5 && p2dist y >= -72) || p2statetype = A
;
trigger1 = statetype = A
trigger1 = ctrl
trigger1 = p2bodydist x = [-const240p(8), (38 + (10 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-72 - 16) * const(size.yscale), (-28 + 72 + (32 * vel y * (vel y > 0))) * const(size.yscale)]
trigger1 = random < (150 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = statetype = A
trigger2 = ctrl
trigger2 = p2bodydist x = [-const240p(8), (38 + (10 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [(-72 - 16) * const(size.yscale), (-28 + 72 + 32 * (vel y > 2.0)) * const(size.yscale)]
trigger2 = p2statetype != A && vel y >= 0.5
trigger2 = random < 300 * (ailevel ** 2.0 / 64.0)

[State -1, AI 600 Jump Light Punch]
type = ChangeState
value = 600
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype = A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
; startup = 4
;Clsn1: 1
;  Clsn1[0] = 22, -55, 37, -20
triggerall = (vel y >= 0.5 && p2dist y >= -50) || p2statetype = A
;
trigger1 = statetype = A
trigger1 = ctrl
trigger1 = p2bodydist x = [-const240p(8), (37 + (7 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-55 - 16) * const(size.yscale), (-20 + 72 + (32 * vel y * (vel y > 0))) * const(size.yscale)]
trigger1 = random < (100 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = statetype = A
trigger2 = ctrl
trigger2 = p2bodydist x = [-const240p(8), (37 + (7 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [(-55 - 16) * const(size.yscale), (-20 + 72 + 32 * (vel y > 2.0)) * const(size.yscale)]
trigger2 = p2statetype != A && vel y >= 0.5
trigger2 = random < 200 * (ailevel ** 2.0 / 64.0)

[State -1, AI 630 Jump Light Kick]
type = ChangeState
value = 630
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype = A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
; startup = 4
;Clsn2Default: 1
;  Clsn2[0] = -10, -106, 31, -35
triggerall = (vel y >= 0.5 && p2dist y >= -50) || p2statetype = A
;
trigger1 = statetype = A
trigger1 = ctrl
trigger1 = p2bodydist x >= (-10 - const(size.ground.front)) * const(size.xscale)
trigger1 = p2bodydist x <= (50 + (4 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [(-106 - 16) * const(size.yscale), (-35 + 72 + (32 * vel y * (vel y > 0))) * const(size.yscale)]
trigger1 = random < ((25 * (ailevel ** 2.0 / 64.0))) || p2bodydist x < 0 || p2statetype = A
trigger1 = random < (100 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = statetype = A
trigger2 = ctrl
trigger2 = p2bodydist x >= (-10 - const(size.ground.front)) * const(size.xscale)
trigger2 = p2bodydist x <= (50 + (4 * (vel x + (enemynear,vel x))) - const(size.ground.front)) * const(size.xscale)
trigger2 = p2dist y = [(-106 - 16) * const(size.yscale), (-35 + 72 + 32 * (vel y > 2.0)) * const(size.yscale)]
trigger2 = p2statetype != A && vel y >= 0.5
trigger2 = random < ((25 * (ailevel ** 2.0 / 64.0))) || p2bodydist x < 0 || p2statetype = A
trigger2 = random < 200 * (ailevel ** 2.0 / 64.0)

;---------------------------------------------------------------------------
;AI Special Moves
;---------------------------------------------------------------------------
[State -1, AI 1000 Skullo Crusher]
type = ChangeState
value = 1000
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = (enemynear, movetype != A) || (enemynear, stateno = [200,499])
triggerall = p2statetype != C
; condition
;Clsn1: 1
;  Clsn1[0] = 23, -72, 54, -40
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x >= (60 * const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [(-72 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [(-77 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 10
trigger2 = p2statetype != A
trigger2 = random < (ailevel * 64.0)

[State -1, AI 1220 Strong Skullo Head]
type = ChangeState
value = 1220
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
; startup = 7
;Clsn1: 1
;  Clsn1[0] = 22, -72, 55, -29
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x >= ((-73 + 7 * enemynear, vel x * (enemynear, statetype = A)) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2bodydist x <= ((73 + 7 * enemynear, vel x * (enemynear, statetype = A)) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [-72 - (8 * enemynear, vel y * (enemynear, vel y > 0)) * const(size.yscale), const240p(8)]
trigger1 = p2stateno != [120, 155]
trigger1 = p2movetype = A || p2statetype = A
trigger1 = enemynear, vel x >= 0 || numtarget
trigger1 = enemynear, vel y >= const240p(-2) || numtarget
trigger1 = random < (150 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-72 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 7
trigger2 = p2statetype != A
trigger2 = movehit
trigger2 = random < (ailevel * 64.0)

[State -1, AI 1210 Medium Skullo Head]
type = ChangeState
value = 1210
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; startup = 7
;Clsn1: 1
;  Clsn1[0] = 22, -72, 55, -29
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x >= ((-73 + 7 * enemynear, vel x * (enemynear, statetype = A)) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2bodydist x <= ((73 + 7 * enemynear, vel x * (enemynear, statetype = A)) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [-72 - (8 * enemynear, vel y * (enemynear, vel y > 0)) * const(size.yscale), const240p(8)]
trigger1 = p2stateno != [120, 155]
trigger1 = p2movetype = A || p2statetype = A
trigger1 = enemynear, vel x >= 0 || numtarget
trigger1 = enemynear, vel y >= const240p(-2) || numtarget
trigger1 = random < (150 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-72 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 7
trigger2 = p2statetype != A
trigger2 = movehit
trigger2 = random < (ailevel * 64.0)

[State -1, AI 1200 Skullo Head]
type = ChangeState
value = 1200
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; startup = 6
;Clsn1: 1
;  Clsn1[0] = 22, -72, 55, -29
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x >= ((-73 + 6 * enemynear, vel x * (enemynear, statetype = A)) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2bodydist x <= ((73 + 6 * enemynear, vel x * (enemynear, statetype = A)) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [-72 - (8 * enemynear, vel y * (enemynear, vel y > 0)) * const(size.yscale), const240p(8)]
trigger1 = p2stateno != [120, 155]
trigger1 = p2movetype = A || p2statetype = A
trigger1 = enemynear, vel x >= 0 || numtarget
trigger1 = enemynear, vel y >= const240p(-2) || numtarget
trigger1 = random < (150 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-72 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 6
trigger2 = p2statetype != A
trigger2 = movehit
trigger2 = random < (ailevel * 64.0)

[State -1, AI 1120 Strong Skullo Slider]
type = ChangeState
value = 1120
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = (enemynear, movetype != A) || (enemynear, stateno = [200,499])
triggerall = p2statetype != A
;Clsn1: 1
;  Clsn1[0] = -1, -20, 61, 0
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = (p2bodydist x >= (80 - const(size.ground.front)) * const(size.xscale)) || backedgebodydist <= const240p(32)
trigger1 = p2bodydist x < (120 - const(size.ground.front)) * const(size.xscale)
trigger1 = p2statetype != A && (enemynear, stateno != [120, 155])
trigger1 = !enemynear, ctrl
trigger1 = p2dist y = [(-20 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (96 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-20 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 5
trigger2 = movehit
trigger2 = random < (ailevel * 64.0)

[State -1, AI 1110 Medium Skullo Slider]
type = ChangeState
value = 1110
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = (enemynear, movetype != A) || (enemynear, stateno = [200,499])
triggerall = p2statetype != A
;Clsn1: 1
;  Clsn1[0] = -1, -20, 61, 0
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = (p2bodydist x >= (65 - const(size.ground.front)) * const(size.xscale)) || backedgebodydist <= const240p(32)
trigger1 = p2bodydist x < (105 - const(size.ground.front)) * const(size.xscale)
trigger1 = p2statetype != A && (enemynear, stateno != [120, 155])
trigger1 = !enemynear, ctrl
trigger1 = p2dist y = [(-20 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (84 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-20 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 5
trigger2 = movehit
trigger2 = random < (150 * (ailevel ** 2.0 / 64.0))

[State -1, AI 1100 Skullo Slider]
type = ChangeState
value = 1100
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = (enemynear, movetype != A) || (enemynear, stateno = [200,499])
;Clsn1: 1
;  Clsn1[0] = -1, -20, 61, 0
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = (p2bodydist x >= (50 - const(size.ground.front)) * const(size.xscale)) || backedgebodydist <= const240p(32)
trigger1 = p2bodydist x < (90 - const(size.ground.front)) * const(size.xscale)
trigger1 = p2statetype != A && (enemynear, stateno != [120, 155])
trigger1 = !enemynear, ctrl
trigger1 = p2dist y = [(-20 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (72 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-20 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 5
trigger2 = movehit
trigger2 = random < (150 * (ailevel ** 2.0 / 64.0))

[State -1, AI 1320 Strong Skullo Dive]
type = ChangeState
value = 1320
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = var(3)!=[1,2]
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
trigger1 = ctrl && pos y <= -30
trigger1 = p2dist y >= (-72 + enemynear,const(size.head.pos.y)) * const(size.yscale)
trigger1 = abs(atan(p2dist y / p2dist x) * (180.0 / pi)) = [8, 24]
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-8, (48 - const(size.ground.front)) - const(size.xscale)]
trigger2 = abs(atan(p2dist y / p2dist x) * (180.0 / pi)) = [8, 24]
trigger2 = enemynear, gethitvar(hittime) >= 8
trigger2 = p2statetype != A
trigger2 = random < (cond(p2statetype != C, 25, 50) * (ailevel ** 2.0 / 64.0))

[State -1, AI 1310 Medium Skullo Dive]
type = ChangeState
value = 1310
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = var(3)!=[1,2]
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
trigger1 = ctrl && pos y <= -30
trigger1 = p2dist y >= (-66 + enemynear,const(size.head.pos.y)) * const(size.yscale)
trigger1 = abs(atan(p2dist y / p2dist x) * (180.0 / pi)) = [32, 64]
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-8, (44 - const(size.ground.front)) - const(size.xscale)]
trigger2 = abs(atan(p2dist y / p2dist x) * (180.0 / pi)) = [32, 64]
trigger2 = enemynear, gethitvar(hittime) >= 8
trigger2 = p2statetype != A
trigger2 = random < (cond(p2statetype != C, 25, 50) * (ailevel ** 2.0 / 64.0))

[State -1, AI 1300 Skullo Dive]
type = ChangeState
value = 1300
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = var(3)!=[1,2]
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
trigger1 = ctrl && pos y <= -30
trigger1 = p2dist y >= (-60 + enemynear,const(size.head.pos.y)) * const(size.yscale)
trigger1 = abs(atan(p2dist y / p2dist x) * (180.0 / pi)) = [40, 80]
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-8, (40 - const(size.ground.front)) - const(size.xscale)]
trigger2 = abs(atan(p2dist y / p2dist x) * (180.0 / pi)) = [40, 80]
trigger2 = enemynear, gethitvar(hittime) >= 7
trigger2 = p2statetype != A
trigger2 = random < (cond(p2statetype != C, 25, 50) * (ailevel ** 2.0 / 64.0))

[State -1, AI 1400 Skullo Face Slam]
type = ChangeState
value = 1400
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = (enemynear, movetype != A) || (enemynear, stateno = [200,499])
; condition
;Clsn2Default: 1
;  Clsn2[0] = -21, -106, 27, -31
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x = [-const240p(8), (240 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2bodydist x > (60 - const(size.ground.front)) * const(size.xscale)
trigger1 = p2statetype = S
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x >= (72 - const(size.ground.front)) * const(size.xscale)
trigger2 = p2statetype = S
trigger2 = moveguarded
trigger2 = random < (25 * (ailevel ** 2.0 / 64.0))

;---------------------------------------------------------------------------
;AI EX Moves
;---------------------------------------------------------------------------
[State -1, AI 1130 EX Skullo Slider]
type = ChangeState
value = 1130
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
triggerall = p2statetype != A
;Clsn1: 1
;  Clsn1[0] = -1, -20, 61, 0
triggerall = (random < (power/10.0)) || var(20) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = (p2bodydist x >= (60 - const(size.ground.front)) * const(size.xscale)) || backedgebodydist <= const240p(32)
trigger1 = p2bodydist x < (120 - const(size.ground.front)) * const(size.xscale)
trigger1 = p2statetype != A && (enemynear, stateno != [120, 155])
trigger1 = !enemynear, ctrl
trigger1 = p2dist y = [(-20 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (96 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-20 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 5
trigger2 = movehit
trigger2 = random < cond(!var(20), (100 * (ailevel ** 2.0 / 64.0)), (ailevel * 48.0))

[State -1, AI 1030 EX Skullo Crusher]
type = ChangeState
value = 1030
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
triggerall = p2statetype != C
; condition
;Clsn1: 1
;  Clsn1[0] = 23, -72, 54, -40
triggerall = (random < (power/10.0)) || var(20) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x >= (60 * const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist x = [-72 * const(size.yscale), 8]
trigger1 = !enemynear, ctrl && (enemynear, stateno != [120, 155])
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-72 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 10
trigger2 = p2statetype != A
trigger2 = movehit
trigger2 = random < cond(!var(20), (50 * (ailevel ** 2.0 / 64.0)), (ailevel * 48.0))

[State -1, AI 1230 EX Skullo Head]
type = ChangeState
value = 1230
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
; startup = 6
;Clsn1: 1
;  Clsn1[0] = 22, -72, 55, -29
triggerall = (random < (power/10.0)) || var(20) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x >= ((-73 + 6 * enemynear, vel x * (enemynear, statetype = A)) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2bodydist x <= ((73 + 6 * enemynear, vel x * (enemynear, statetype = A)) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [-72 - (8 * enemynear, vel y * (enemynear, vel y > 0)) * const(size.yscale), const240p(8)]
trigger1 = p2stateno != [120, 155]
trigger1 = p2movetype = A || p2statetype = A
trigger1 = enemynear, vel x >= 0 || numtarget
trigger1 = enemynear, vel y >= const240p(-2) || numtarget
trigger1 = random < ((cond(var(20), 250, 150) * (ailevel ** 2.0 / 64.0)))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-72 * const(size.yscale), const240p(8)]
trigger2 = enemynear, gethitvar(hittime) >= 6
trigger2 = p2statetype != A
trigger2 = movehit
trigger2 = random < cond(!var(20), (50 * (ailevel ** 2.0 / 64.0)), (ailevel * 48.0))

[State -1, AI 1330 EX Skullo Dive]
type = ChangeState
value = 1330
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype = A
triggerall = var(3)!=[1,2]
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
;
triggerall = (random < (power/10.0)) || var(20) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
; condition
trigger1 = ctrl && pos y <= -30
trigger1 = p2dist y >= (-72 + enemynear,const(size.head.pos.y)) * const(size.yscale)
trigger1 = abs(atan(p2dist y / p2dist x) * (180.0 / pi)) = [8, 24]
trigger1 = !enemynear, ctrl && (enemynear, stateno != [120, 155])
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(5)
trigger2 = p2bodydist x = [-8, (48 - const(size.ground.front)) - const(size.xscale)]
trigger2 = abs(atan(p2dist y / p2dist x) * (180.0 / pi)) = [8, 24]
trigger2 = enemynear, gethitvar(hittime) >= 8
trigger2 = p2statetype != A
trigger2 = movehit
trigger2 = random < (cond(p2statetype != C, 25, 50) * (ailevel ** 2.0 / 64.0))

[State -1, AI 1430 EX Skullo Face Slam]
type = ChangeState
value = 1430
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = ifelse(var(20) <= 0, power >= 500, power >= 0)
; condition
;Clsn2Default: 1
;  Clsn2[0] = -21, -106, 27, -31
triggerall = (random < (power/10.0)) || var(20) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x >= (72 - const(size.ground.front)) * const(size.xscale)
trigger1 = p2statetype != A
trigger1 = !enemynear, ctrl && (enemynear, stateno != [120, 155])
trigger1 = random < ((cond(var(20), 75, 25) * (ailevel ** 2.0 / 64.0)))
; condition
trigger2 = var(5)
trigger2 = moveguarded
trigger2 = random < (25 * (ailevel ** 2.0 / 64.0))

;---------------------------------------------------------------------------
;AI Super Moves
;---------------------------------------------------------------------------
[State -1, AI 3600 Neo Skullo Dream]
type = ChangeState
value = 3600
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
;
triggerall = ifelse(var(20) <= 0, power >= 3000, power >= 1000)
triggerall = enemynear, life >= 0.20 * enemynear, lifemax
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2dist x = [16 , (160 - const(size.ground.front)) * const(size.xscale)]
trigger1 = !(enemynear, ctrl) && (p2stateno != 40) && (p2stateno != 105) && (p2stateno != [5030, 5119])
trigger1 = p2statetype != A && (p2dist y = 0)
trigger1 = enemynear, vel x <= 0
trigger1 = random < (100 * (ailevel ** 2.0 / 64.0))
;
trigger2 = var(6)
trigger2 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = 0
trigger2 = enemynear, gethitvar(hittime) >= 6
trigger2 = p2statetype != A
trigger2 = random < (25 * (ailevel ** 2.0 / 64.0))

trigger3 = (StateNo =[200,250]) && StateNo != 222
trigger3 = var(6)
trigger3 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger3 = p2dist y = 0
trigger3 = enemynear, gethitvar(hittime) >= 6
trigger3 = p2statetype != A
trigger3 = random < (25 * (ailevel ** 2.0 / 64.0))

[State -1, AI 3600 Neo Skullo Dream(Alternate)]
type = ChangeState
value = 3600
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = ifelse(var(20) <= 0, power >= 3000, power >= 1000)
;
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = enemynear, life >= 0.20 * enemynear, lifemax
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2dist x = [16 , (160 - const(size.ground.front)) * const(size.xscale)]
trigger1 = !(enemynear, ctrl) && (p2stateno != 40) && (p2stateno != 105) && (p2stateno != [5030, 5119])
trigger1 = p2statetype != A && (p2dist y = 0)
trigger1 = enemynear, vel x <= 0
trigger1 = random < (100 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(6)
trigger2 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = 0
trigger2 = enemynear, gethitvar(hittime) >= 6
trigger2 = p2statetype != A
trigger2 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = (StateNo =[200,250]) && StateNo != 222
trigger3 = var(6)
trigger3 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger3 = p2dist y = 0
trigger3 = enemynear, gethitvar(hittime) >= 6
trigger3 = p2statetype != A
trigger3 = random < (25 * (ailevel ** 2.0 / 64.0))

[State -1, AI 3500 Skullo Dream]
type = ChangeState
value = 3500
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = ifelse(var(20) <= 0, power >= 3000, power >= 1000)
;
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = enemynear, life >= 0.20 * enemynear, lifemax
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2dist x = [16 , (160 - const(size.ground.front)) * const(size.xscale)]
trigger1 = !(enemynear, ctrl) && (p2stateno != 40) && (p2stateno != 105) && (p2stateno != [5030, 5119])
trigger1 = p2statetype != A && (p2dist y = 0)
trigger1 = enemynear, vel x <= 0
trigger1 = random < (100 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(6)
trigger2 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = 0
trigger2 = enemynear, gethitvar(hittime) >= 6
trigger2 = p2statetype != A
trigger2 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = (StateNo =[200,250]) && StateNo != 222
trigger3 = var(6)
trigger3 = p2bodydist x = [-const240p(8), (40 - const(size.ground.front)) * const(size.xscale)]
trigger3 = p2dist y = 0
trigger3 = enemynear, gethitvar(hittime) >= 6
trigger3 = p2statetype != A
trigger3 = random < (25 * (ailevel ** 2.0 / 64.0))

[State -1, AI 3300 Skullo Energy]
type = ChangeState
value = 3300
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101]) || var(6)
triggerall = !numhelper(3305)
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
;Clsn1Default: 1
;  Clsn1[0] = -(49, -88, 47, 15) * 0.8
triggerall = (random < (50 * (ailevel ** 2.0 / 64.0))) || (power >= 2000) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = !(enemynear, ctrl) && ((enemynear, stateno != [120, 155]) || enemynear, statetype = A)
; condition
trigger1 = NumHelper(3305) <= 0
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101]) 
trigger1 = p2bodydist x >= ((-49 + (6 * enemynear, vel x * (enemynear, statetype = A))) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2bodydist x <= ((49 + (6 * enemynear, vel x * (enemynear, statetype = A))) - const(size.ground.front)) * const(size.xscale)
trigger1 = p2dist y = [(-122 - (((enemynear, vel y) + (6 * enemynear, const(movement.yaccel))) * (p2statetype = A))) * const(size.yscale), const240p(8)]
trigger1 = enemynear, vel x >= 0
trigger1 = enemynear, vel y > const240p(-1)
trigger1 = p2movetype = A || (p2statetype = A && (enemynear, stateno != [120, 155]))
trigger1 = (p2bodydist x > 0) && (facing != enemynear, facing)
trigger1 = random < (cond(p2statetype != A, 25, 100) * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = NumHelper(3305) <= 0
trigger2 = var(6)
trigger2 = stateno = 1030
trigger2 = movehit && numtarget
trigger2 = random < (300 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = NumHelper(3305) = 1
trigger3 = Helper(3305),StateNo=3205
trigger3 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101]) 
trigger3 = p2bodydist x = [-49 + (6 * enemynear, vel x), ((47 + (6 * enemynear, vel x)) - const(size.ground.front)) * const(size.xscale)]
trigger3 = p2dist y = [(-88 - (enemynear, vel y))* const(size.yscale), const240p(8)]
trigger3 = enemynear, vel x >= 0
trigger3 = enemynear, vel y > const240p(-1)
trigger3 = p2movetype = A || (p2statetype = A && (enemynear, stateno != [120, 155]))
trigger3 = (p2bodydist x > 0) && (facing != enemynear, facing)
trigger3 = random < (cond(p2statetype != A, 25, 100) * (ailevel ** 2.0 / 64.0))
; condition
trigger4 = NumHelper(3305) = 1
trigger4 = Helper(3305),StateNo=3205
trigger4 = var(6)
trigger4 = stateno = 1030
trigger4 = movehit && numtarget
trigger4 = random < (200 * (ailevel ** 2.0 / 64.0))

[State -1, AI 3060 Air Super Skullo Crusher Max]
type = ChangeState
value = 3060
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = RoundState = 2 && StateType = A
triggerall = ifelse(var(20) <= 0, power >= 2000, power >= 1000)
triggerall = var(3)!=[1,2]
;
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = p2statetype != C
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = !(enemynear, ctrl) && ((enemynear, stateno != [120, 155]) || enemynear, statetype = A)
; condition
;Clsn1: 1
;  Clsn1[0] = 16, -76, 54, -32
triggerall = enemynear, life >= 0.15 * enemynear, lifemax
; condition
trigger1 = ctrl && pos y < -35
trigger1 = p2bodydist x = [-const240p(8), (96 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [-76 - (enemynear, vel y) * const(size.yscale), -32 - enemynear, vel y * (enemynear, vel y > 0)]
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(6) || var(7)
trigger2 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y >= (-76 + ((7 * (vel y + enemynear,vel y)) * (vel y != 0))) * const(size.yscale)
trigger2 = p2dist y <= ((-32 + ((7 * (vel y + enemynear,vel y)) * (vel y > 0))) - enemynear,const(size.mid.pos.y)) * const(size.yscale)
trigger2 = movehit
trigger2 = (enemynear, gethitvar(hittime) >= 7) || (enemynear, hitfall)
trigger2 = random < (ailevel * 64.0)

[State -1, AI 3050 Super Skullo Crusher Max]
type = ChangeState
value = 3050
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = ifelse(var(20) <= 0, power >= 2000, power >= 1000)
;
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = p2statetype != C
triggerall = enemynear, life >= 0.15 * enemynear, lifemax
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = !(enemynear, ctrl) && ((enemynear, stateno != [120, 155]) || enemynear, statetype = A)
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x = [-const240p(8), (96 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [-76 - (enemynear, vel y * (enemynear, vel y > 0)) * const(size.yscale), const240p(8)]
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))

trigger2 = var(6) || var(7)
trigger2 = p2bodydist x = [-const240p(8), (96 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-23 * const(size.yscale), const240p(8)]
trigger2 = movehit
trigger2 = (enemynear, gethitvar(hittime) >= 7) || (enemynear, gethitvar(yvel) != 0)
trigger2 = !(stateno = 3100 && animelemtime(17) < 0)
trigger2 = random < (cond((hitdefattr = SCA, NA), 100 * (ailevel ** 2.0 / 64.0), (ailevel * 64.0))) + (2 * (ailevel ** 2.0))

[State -1, AI 3150 Super Skullo Slider Max]
type = ChangeState
value = 3150
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = ifelse(var(20) <= 0, power >= 2000, power >= 1000)
;
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = !(enemynear, ctrl) && ((enemynear, stateno != [120, 155]) || enemynear, statetype = A)
;Clsn1: 1
;  Clsn1[0] = -2, -23, 72, 0
triggerall = enemynear, life >= 0.15 * enemynear, lifemax
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x = [-const240p(8), (96 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-23 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = (p2stateno != [120, 155]) || (enemynear, hitdefattr = SCA, NA)
trigger1 = !enemynear, ctrl
trigger1 = enemynear, animtime < -12
trigger1 = random < (75 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(6) || var(7)
trigger2 = p2bodydist x = [-const240p(8), (96 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-23 * const(size.yscale), const240p(8)]
trigger2 = movehit
trigger2 = enemynear, gethitvar(hittime) >= 8
trigger2 = p2statetype != A
trigger2 = !(stateno = 3100 && animelemtime(17) < 0)
trigger2 = random < (cond((hitdefattr = SCA, NA), 100 * (ailevel ** 2.0 / 64.0), (ailevel * 64.0))) + (2 * (ailevel ** 2.0))

[State -1, AI 3200 Skullo Ball]
type = ChangeState
value = 3200
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = NumHelper(3205) <= 1
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
;
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = (random < (50 * (ailevel ** 2.0 / 64.0))) || (power >= 2000) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x >= 160
trigger1 = enemynear, movetype != A
trigger1 = enemynear, vel x <= 0
trigger1 = random < (3 ** (floor(power / 600.0)))
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger2 = enemynear, stateno = 5110
trigger2 = enemynear, time < enemynear, const(data.liedown.time) - 20
trigger2 = random < (3 ** (floor(power / 600.0)))
trigger2 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = var(6)
trigger3 = stateno = 1030
trigger3 = movehit && numtarget
trigger3 = random < (250 * (ailevel ** 2.0 / 64.0))

[State -1, AI 3100 Super Skullo Slider]
type = ChangeState
value = 3100
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
;Clsn1: 1
;  Clsn1[0] = -2, -23, 72, 0
triggerall = (random < (50 * (ailevel ** 2.0 / 64.0))) || (power >= 2000) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = !(enemynear, ctrl) && ((enemynear, stateno != [120, 155]) || enemynear, statetype = A)
triggerall = p2statetype != A
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-23 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = (p2stateno != [120, 155]) || (enemynear, hitdefattr = SCA, NA)
trigger1 = !enemynear, ctrl
trigger1 = enemynear, animtime < -12
trigger1 = random < (75 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(6)
trigger2 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-23 * const(size.yscale), const240p(8)]
trigger2 = movehit
trigger2 = enemynear, gethitvar(hittime) >= 8
trigger2 = p2statetype != A
trigger2 = random < (cond((hitdefattr = SCA, NA), 200 * (ailevel ** 2.0 / 64.0), (ailevel * 64.0)))

[State -1, AI 3010 Air Super Skullo Crusher]
type = ChangeState
value = 3010
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = RoundState = 2 && StateType = A
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
triggerall = var(3)!=[1,2]
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
; condition
;Clsn1: 1
;  Clsn1[0] = 16, -76, 54, -32
triggerall = (random < (50 * (ailevel ** 2.0 / 64.0))) || (power >= 2000) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
triggerall = !(enemynear, ctrl) && ((enemynear, stateno != [120, 155]) || enemynear, statetype = A)
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = p2statetype != C
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
; condition
trigger1 = ctrl && pos y < -35
trigger1 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [-76 - (enemynear, vel y) * const(size.yscale), -32 - enemynear, vel y * (enemynear, vel y > 0)]
trigger1 = random < (25 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(6)
trigger2 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y >= (-76 + ((7 * (vel y + enemynear,vel y)) * (vel y != 0))) * const(size.yscale)
trigger2 = p2dist y <= ((-32 + ((7 * (vel y + enemynear,vel y)) * (vel y > 0))) - enemynear,const(size.mid.pos.y)) * const(size.yscale)
trigger2 = movehit
trigger2 = (enemynear, gethitvar(hittime) >= 7) || (enemynear, hitfall)
trigger2 = random < (ailevel * 64.0)

[State -1, AI 3000 Super Skullo Crusher]
type = ChangeState
value = 3000
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = !(enemynear, ctrl) && ((enemynear, stateno != [120, 155]) || enemynear, statetype = A)
triggerall = ifelse(var(20) <= 0, power >= 1000, power >= 0)
triggerall = (enemynear, const(size.head.pos.y) <= -40) || (enemynear, statetype = A)
triggerall = p2statetype != C
;Clsn1: 1
;  Clsn1[0] = 16, -76, 54, -32
triggerall = (random < (50 * (ailevel ** 2.0 / 64.0))) || (power >= 2000) || ((life/lifemax * 1.0) < 0.9 * (enemynear, life/enemynear, lifemax * 1.0)) || (life < 0.25 * lifemax)
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
; condition
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-76 - (enemynear, vel y * (enemynear, vel y > 0))) * const(size.yscale), const240p(8)]
trigger1 = (p2stateno != [120, 155]) || (enemynear, hitdefattr = SCA, NA)
trigger1 = !enemynear, ctrl
trigger1 = enemynear, animtime < -10
trigger1 = random < (50 * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = var(6)
trigger2 = p2bodydist x = [-const240p(8), (108 - const(size.ground.front)) * const(size.xscale)]
trigger2 = p2dist y = [-76 * const(size.yscale), const240p(8)]
trigger2 = movehit
trigger2 = (enemynear, gethitvar(hittime) >= 7) || (enemynear, gethitvar(yvel) != 0)
trigger2 = random < (cond((hitdefattr = SCA, NA), 200 * (ailevel ** 2.0 / 64.0), (ailevel * 64.0)))

[State -1, AI 3400 Super Skullo Energy]
type = ChangeState
value = 3400
triggerall = ailevel
triggerall = numenemy
triggerall = p2statetype != L && p2stateno != 5120 && p2stateno != 5201
triggerall = !var(16) && (var(15) < 1)
triggerall = roundstate = 2 && statetype != A
triggerall = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101]) || var(6) || var(7)
triggerall = !((enemynear, movetype = H) && (enemynear, stateno = 1420))
triggerall = ifelse(var(20) <= 0, power >= 2000, power >= 1000)
;Clsn1Default: 1
;  Clsn1[0] = -(49, -88, 47, 15) * 0.8
triggerall = enemynear, life >= 0.15 * enemynear, lifemax
triggerall = !(((stateno = [200,699]) && Time <= 2) && numtarget)
; condition
trigger1 = NumHelper(3405) <= 0
trigger1 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger1 = p2bodydist x = [-49 + (6 * enemynear, vel x), ((47 + (6 * enemynear, vel x)) - const(size.ground.front)) * const(size.xscale)]
trigger1 = p2dist y = [(-88 - (enemynear, vel y))* const(size.yscale), const240p(8)]
trigger1 = enemynear, vel x >= 0
trigger1 = enemynear, vel y > const240p(-1)
trigger1 = p2movetype = A || (p2statetype = A && (enemynear, stateno != [120, 155]))
trigger1 = (p2bodydist x > 0) && (facing != enemynear, facing)
trigger1 = random < (cond(p2statetype != A, 25, 100) * (ailevel ** 2.0 / 64.0))
; condition
trigger2 = NumHelper(3405) <= 0
trigger2 = var(6) || var(7)
trigger2 = stateno = 1030
trigger2 = movehit && numtarget
trigger2 = random < (300 * (ailevel ** 2.0 / 64.0))
; condition
trigger3 = NumHelper(3405) = 1
trigger3 = Helper(3405),StateNo=3205
trigger3 = ctrl || StateNo = 40 || StateNo = 52 || (StateNo = [100,101])
trigger3 = p2bodydist x = [-49 + (6 * enemynear, vel x), ((47 + (6 * enemynear, vel x)) - const(size.ground.front)) * const(size.xscale)]
trigger3 = p2dist y = [(-88 - (enemynear, vel y))* const(size.yscale), const240p(8)]
trigger3 = enemynear, vel x >= 0
trigger3 = enemynear, vel y > const240p(-1)
trigger3 = p2movetype = A || (p2statetype = A && (enemynear, stateno != [120, 155]))
trigger3 = (p2bodydist x > 0) && (facing != enemynear, facing)
trigger3 = random < (cond(p2statetype != A, 25, 100) * (ailevel ** 2.0 / 64.0))
; condition
trigger4 = NumHelper(3405) = 1
trigger4 = Helper(3405),StateNo=3205
trigger4 = var(6) || var(7)
trigger4 = stateno = 1030
trigger4 = movehit && numtarget
trigger4 = random < (300 * (ailevel ** 2.0 / 64.0))

;============================================================================
; AI Taunts -----------------------------------------------------------------
;============================================================================
[State -1, AI 195 Taunt]
type = changestate
value = 195
triggerall = ailevel && numenemy && roundstate = 2
triggerall = statetype != A
triggerall = ctrl
triggerall = life >= (enemynear, life)
triggerall = StateNo != [200,699]
trigger1 = p2dist x > 192 && (enemynear, vel y > 0)
trigger1 = !(enemynear, ctrl) && (enemynear, movetype = H)
trigger1 = random < (10 * (AIlevel ** 2.0 / 64.0))