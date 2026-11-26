package com.nexora.gamepad

import android.app.Activity
import android.graphics.Canvas
import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.Paint
import android.os.Bundle
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.TextView
import org.json.JSONArray
import org.json.JSONObject
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketTimeoutException
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread
import kotlin.math.min

class MainActivity : Activity() {
    private val port = 26760
    @Volatile private var host = "192.168.1.100"
    @Volatile private var connected = false
    @Volatile private var lastResponseAt = 0L
    @Volatile private var lastHelloAt = 0L
    @Volatile private var rejectedByServer = false
    @Volatile private var pairingCode = ""
    @Volatile private var running = false
    private var socket: DatagramSocket? = null
    private var sender: ScheduledExecutorService? = null
    private val lock = Any()
    private val pressed = mutableSetOf<String>()
    private val axes = mutableMapOf("leftX" to 0.0, "leftY" to 0.0, "rightX" to 0.0, "rightY" to 0.0, "leftTrigger" to 0.0, "rightTrigger" to 0.0)
    private lateinit var status: TextView
    private lateinit var ipField: EditText
    private lateinit var codeField: EditText
    private lateinit var connectButton: Button
    private var haptics = true
    private var stickSensitivity = 1.0f
    private var stickDeadzone = 0.08f
    private var transport = "WIFI"
    private lateinit var transportHelp: TextView
    private val transportButtons = mutableMapOf<String, Button>()
    private val profileButtons = mutableMapOf<String, Button>()
    private var activeProfile = "GENERAL"
    private lateinit var sensitivityControl: SeekBar
    private lateinit var deadzoneControl: SeekBar

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.decorView.systemUiVisibility = 5894 or 1024 or 512 or 4096
        val preferences = getSharedPreferences("nexora_settings", MODE_PRIVATE)
        host = preferences.getString("pc_ip", host) ?: host
        haptics = preferences.getBoolean("haptics", true)
        transport = preferences.getString("transport", "WIFI") ?: "WIFI"
        activeProfile = preferences.getString("active_profile", "GENERAL") ?: "GENERAL"
        val profileDefaults = profileValues(activeProfile)
        stickSensitivity = preferences.getFloat("profile_${activeProfile}_sensitivity", profileDefaults.first)
        stickDeadzone = preferences.getFloat("profile_${activeProfile}_deadzone", profileDefaults.second)
        buildInterface()
    }

    private fun buildInterface() {
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(8, 4, 8, 4); setBackgroundColor(Color.rgb(12, 16, 25)) }
        val header = LinearLayout(this).apply { gravity = Gravity.CENTER_VERTICAL }
        header.addView(TextView(this).apply { text = "NEXORA GAMEPAD"; textSize = 17f; setTextColor(Color.WHITE) }, LinearLayout.LayoutParams(0, 34, 1f))
        status = TextView(this).apply { text = "● SIN CONEXIÓN"; textSize = 12f; setTextColor(Color.rgb(255, 190, 90)) }
        header.addView(status); root.addView(header)

        val connection = LinearLayout(this).apply { gravity = Gravity.CENTER_VERTICAL }
        ipField = EditText(this).apply { setSingleLine(true); setText(host); hint = "IP local de tu PC"; textSize = 14f; setTextColor(Color.WHITE); setHintTextColor(Color.LTGRAY) }
        connection.addView(ipField, LinearLayout.LayoutParams(0, 28, 1f))
        connectButton = Button(this).apply { text = "CONECTAR"; setOnClickListener { connectToPc() } }
        connection.addView(connectButton); root.addView(connection)
        codeField = EditText(this).apply {
            setSingleLine(true)
            hint = "Código de emparejamiento de Windows (6 dígitos)"
            inputType = android.text.InputType.TYPE_CLASS_NUMBER
            textSize = 13f
            setTextColor(Color.WHITE)
            setHintTextColor(Color.LTGRAY)
        }
        root.addView(codeField, LinearLayout.LayoutParams(-1, 36))
        root.addView(TextView(this).apply { text = "Elige cómo conectar el teléfono al PC"; textSize = 10f; setTextColor(Color.LTGRAY); gravity = Gravity.CENTER })
        val transportRow = LinearLayout(this).apply { gravity = Gravity.CENTER }
        val transportOptions = listOf("WIFI" to "WI-FI", "USB" to "USB", "BLUETOOTH" to "BLUETOOTH")
        transportOptions.forEach { (key, label) ->
            val option = Button(this).apply {
                text = label
                textSize = 10f
                setOnClickListener {
                    transport = key
                    getSharedPreferences("nexora_settings", MODE_PRIVATE).edit().putString("transport", transport).apply()
                    updateTransportHelp()
                }
            }
            transportButtons[key] = option
            transportRow.addView(option, LinearLayout.LayoutParams(0, 34, 1f))
        }
        root.addView(transportRow)
        transportHelp = TextView(this).apply { textSize = 9f; setTextColor(Color.rgb(150,190,220)); gravity = Gravity.CENTER }
        root.addView(transportHelp, LinearLayout.LayoutParams(-1, 28))
        updateTransportHelp()

        val profileRow = LinearLayout(this).apply { gravity = Gravity.CENTER }
        listOf("GENERAL" to "GENERAL", "PPSSPP" to "PPSSPP", "ACCION" to "ACCIÓN", "PERSONAL" to "PERSONAL").forEach { (key, label) ->
            val profileButton = Button(this).apply {
                text = label
                textSize = 9f
                setOnClickListener { applyProfile(key) }
            }
            profileButtons[key] = profileButton
            profileRow.addView(profileButton, LinearLayout.LayoutParams(0, 32, 1f))
        }
        root.addView(profileRow)

        val tuning = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        val sensitivityLabel = TextView(this).apply { text = "Sensibilidad"; textSize = 11f; setTextColor(Color.WHITE) }
        tuning.addView(sensitivityLabel)
        sensitivityControl = SeekBar(this).apply {
            max = 100
            progress = ((stickSensitivity - 0.5f) * 100f).toInt().coerceIn(0,100)
            setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    stickSensitivity = 0.5f + progress / 100f
                    getSharedPreferences("nexora_settings", MODE_PRIVATE).edit().putFloat("profile_${activeProfile}_sensitivity", stickSensitivity).apply()
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })
        }
        tuning.addView(sensitivityControl, LinearLayout.LayoutParams(0, 38, 1f))
        val deadzoneLabel = TextView(this).apply { text = "Zona muerta"; textSize = 11f; setTextColor(Color.WHITE) }
        tuning.addView(deadzoneLabel)
        deadzoneControl = SeekBar(this).apply {
            max = 25
            progress = (stickDeadzone * 100f).toInt().coerceIn(0,25)
            setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    stickDeadzone = progress / 100f
                    getSharedPreferences("nexora_settings", MODE_PRIVATE).edit().putFloat("profile_${activeProfile}_deadzone", stickDeadzone).apply()
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })
        }
        tuning.addView(deadzoneControl, LinearLayout.LayoutParams(0, 38, 1f))
        root.addView(tuning)

        val shoulders = LinearLayout(this).apply { gravity = Gravity.CENTER }
        listOf(Triple("L1","LB",1f), Triple("L2","LT",1f), Triple("SELECT","BACK",1f), Triple("START","START",1f), Triple("R2","RT",1f), Triple("R1","RB",1f)).forEach {
            shoulders.addView(controlButton(it.first,it.second), LinearLayout.LayoutParams(0,36,it.third))
        }
        root.addView(shoulders)

        val game = LinearLayout(this).apply { gravity = Gravity.CENTER }
        val left = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER }
        val stickSize = (resources.displayMetrics.heightPixels * 0.36f).toInt().coerceIn(108,150)
        left.addView(JoystickView("leftX","leftY"), LinearLayout.LayoutParams(stickSize,stickSize))
        left.addView(dpad(), LinearLayout.LayoutParams(stickSize,92))
        game.addView(left, LinearLayout.LayoutParams(0,-1,1f))

        val center = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER }
        center.addView(controlButton("L3","LS"), LinearLayout.LayoutParams(64,34))
        center.addView(JoystickView("rightX","rightY"), LinearLayout.LayoutParams((stickSize * 0.78f).toInt(),(stickSize * 0.78f).toInt()))
        center.addView(controlButton("R3","RS"), LinearLayout.LayoutParams(70,44))
        game.addView(center, LinearLayout.LayoutParams(0,-1,1f))

        val face = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER }
        val row1 = LinearLayout(this).apply { gravity = Gravity.CENTER }; row1.addView(controlButton("Y","Y"), LinearLayout.LayoutParams(54,48))
        val row2 = LinearLayout(this).apply { gravity = Gravity.CENTER }; row2.addView(controlButton("X","X"), LinearLayout.LayoutParams(68,60)); row2.addView(controlButton("B","B"), LinearLayout.LayoutParams(68,60))
        val row3 = LinearLayout(this).apply { gravity = Gravity.CENTER }; row3.addView(controlButton("A","A"), LinearLayout.LayoutParams(68,60))
        face.addView(row1); face.addView(row2); face.addView(row3)
        game.addView(face, LinearLayout.LayoutParams(0,-1,1f))
        root.addView(game, LinearLayout.LayoutParams(-1,0,1f))

        val footer = LinearLayout(this).apply { gravity = Gravity.CENTER }
        footer.addView(Button(this).apply { text = if (haptics) "VIBRACIÓN: ACTIVADA" else "VIBRACIÓN: DESACTIVADA"; setOnClickListener { haptics = !haptics; getSharedPreferences("nexora_settings", MODE_PRIVATE).edit().putBoolean("haptics", haptics).apply(); text = if (haptics) "VIBRACIÓN: ACTIVADA" else "VIBRACIÓN: DESACTIVADA" } })
        footer.addView(Button(this).apply { text = "DESCONECTAR"; setOnClickListener { disconnect("Desconectado") } })
        root.addView(footer)
        setContentView(root)
        applyProfile(activeProfile)
    }

    private fun profileValues(profile: String): Pair<Float, Float> = when (profile) {
        "PPSSPP" -> Pair(1.15f, 0.05f)
        "ACCION" -> Pair(0.95f, 0.12f)
        "PERSONAL" -> Pair(1.0f, 0.08f)
        else -> Pair(1.0f, 0.08f)
    }

    private fun applyProfile(profile: String) {
        activeProfile = profile
        val preferences = getSharedPreferences("nexora_settings", MODE_PRIVATE)
        val defaults = profileValues(profile)
        stickSensitivity = preferences.getFloat("profile_${profile}_sensitivity", defaults.first)
        stickDeadzone = preferences.getFloat("profile_${profile}_deadzone", defaults.second)
        preferences.edit().putString("active_profile", profile).apply()
        if (::sensitivityControl.isInitialized) sensitivityControl.progress = ((stickSensitivity - 0.5f) * 100f).toInt().coerceIn(0, 100)
        if (::deadzoneControl.isInitialized) deadzoneControl.progress = (stickDeadzone * 100f).toInt().coerceIn(0, 25)
        profileButtons.forEach { (key, button) ->
            val selected = key == profile
            button.backgroundTintList = ColorStateList.valueOf(
                if (selected) Color.rgb(30, 115, 170) else Color.rgb(45, 53, 68)
            )
            button.setTextColor(Color.WHITE)
            button.alpha = if (selected) 1.0f else 0.78f
        }
    }

    private fun updateTransportHelp() {
        if (!::transportHelp.isInitialized) return
        transportHelp.text = when (transport) {
            "USB" -> "USB: conecta el cable y activa Anclaje USB en Android."
            "BLUETOOTH" -> "Bluetooth: empareja el PC y activa Anclaje Bluetooth."
            else -> "Wi-Fi: ambos equipos deben usar la misma red local."
        }
        transportButtons.forEach { (key, button) ->
            val selected = key == transport
            button.backgroundTintList = ColorStateList.valueOf(
                if (selected) Color.rgb(30, 115, 170) else Color.rgb(45, 53, 68)
            )
            button.setTextColor(Color.WHITE)
            button.alpha = if (selected) 1.0f else 0.78f
        }
    }
    private fun dpad(): View {
        val box = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER }
        box.addView(controlButton("↑","UP"), LinearLayout.LayoutParams(48,30))
        val row = LinearLayout(this).apply { gravity = Gravity.CENTER }
        listOf(Triple("←","LEFT",0),Triple("↓","DOWN",1),Triple("→","RIGHT",2)).forEach { row.addView(controlButton(it.first,it.second), LinearLayout.LayoutParams(56,36)) }
        box.addView(row); return box
    }

    private fun controlButton(label: String, key: String) = Button(this).apply {
        text = label; textSize = 13f
        setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> { synchronized(lock) { if (key == "LT") axes["leftTrigger"] = 1.0 else if (key == "RT") axes["rightTrigger"] = 1.0 else pressed.add(key) }; vibrateTap(); true }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> { synchronized(lock) { if (key == "LT") axes["leftTrigger"] = 0.0 else if (key == "RT") axes["rightTrigger"] = 0.0 else pressed.remove(key) }; true }
                else -> true
            }
        }
    }

    private inner class JoystickView(private val xName: String, private val yName: String) : View(this@MainActivity) {
        private val base = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.rgb(37,48,67) }
        private val ring = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.rgb(100,125,155); style = Paint.Style.STROKE; strokeWidth = 5f }
        private val knob = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.rgb(30,170,220) }
        private var nx = 0f; private var ny = 0f
        override fun onDraw(canvas: Canvas) {
            val cx = width/2f; val cy = height/2f; val r = min(width,height)*0.39f
            canvas.drawCircle(cx,cy,r,base); canvas.drawCircle(cx,cy,r,ring)
            canvas.drawCircle(cx+nx*r*0.68f,cy+ny*r*0.68f,r*0.36f,knob)
        }
        override fun onTouchEvent(event: MotionEvent): Boolean {
            val cx=width/2f; val cy=height/2f; val r=min(width,height)*0.39f
            if (event.action == MotionEvent.ACTION_UP || event.action == MotionEvent.ACTION_CANCEL) { nx=0f; ny=0f }
            else {
                val rawX=((event.x-cx)/r).coerceIn(-1f,1f)
                val rawY=((event.y-cy)/r).coerceIn(-1f,1f)
                fun tune(value: Float): Float {
                    val magnitude = kotlin.math.abs(value)
                    if (magnitude <= stickDeadzone) return 0f
                    val adjusted = ((magnitude - stickDeadzone) / (1f - stickDeadzone)).coerceIn(0f,1f)
                    return (kotlin.math.sign(value) * adjusted * stickSensitivity).coerceIn(-1f,1f)
                }
                nx=tune(rawX); ny=tune(rawY)
            }
            synchronized(lock) { axes[xName]=nx.toDouble(); axes[yName]=ny.toDouble() }
            invalidate(); return true
        }
    }

    private fun connectToPc() {
        val candidate=ipField.text.toString().trim()
        try { InetAddress.getByName(candidate) } catch (_: Exception) { status.text="● IP NO VÁLIDA"; return }
        val enteredCode = codeField.text.toString().trim()
        if (!enteredCode.matches(Regex("\\d{6}"))) { status.text="● INTRODUCE EL CÓDIGO DE 6 DÍGITOS"; return }
        disconnect(null); host=candidate; pairingCode=enteredCode
        getSharedPreferences("nexora_settings", MODE_PRIVATE).edit().putString("pc_ip", host).apply()
        running=true
        rejectedByServer=false
        lastHelloAt=0L
        try { socket=DatagramSocket().apply { soTimeout=500 } } catch (_: Exception) { running=false; status.text="● ERROR AL ABRIR RED"; return }
        status.text="● BUSCANDO PC..."; connectButton.text="BUSCANDO..."
        thread(name="Nexora-Receiver") {
            val buffer=ByteArray(1024)
            while (running) {
                try {
                    val packet=DatagramPacket(buffer,buffer.size); socket?.receive(packet)
                    val response=JSONObject(String(packet.data,0,packet.length,Charsets.UTF_8))
                    if (packet.address.hostAddress == InetAddress.getByName(host).hostAddress) {
                        when (response.optString("type")) {
                            "busy" -> {
                                rejectedByServer = true
                                connected = false
                                runOnUiThread {
                                    status.text = "● LÍMITE DE TELÉFONOS ALCANZADO"
                                    status.setTextColor(Color.rgb(255, 150, 90))
                                    connectButton.text = "REINTENTAR"
                                }
                            }
                            "hello_ack", "input_ack" -> {
                                connected = true
                                lastResponseAt = System.currentTimeMillis()
                                val peer = packet.address.hostAddress ?: host
                                runOnUiThread {
                                    status.text = "● CONECTADO A " + peer
                                    status.setTextColor(Color.rgb(90, 220, 145))
                                    connectButton.text = "CONECTADO"
                                }
                            }
                        }
                    }
                } catch (_: SocketTimeoutException) { } catch (_: Exception) { if (running) runOnUiThread { status.text="● ERROR DE RED" } }
            }
        }
        sender=Executors.newSingleThreadScheduledExecutor()
        sender?.scheduleAtFixedRate({
            if (running) {
                if (connected && System.currentTimeMillis() - lastResponseAt > 2500) {
                    connected = false
                    runOnUiThread { status.text = "● PC SIN RESPUESTA"; status.setTextColor(Color.rgb(255,190,90)); connectButton.text = "REINTENTANDO..." }
                }
                if (connected) sendState() else if (!rejectedByServer && System.currentTimeMillis() - lastHelloAt >= 700) { lastHelloAt = System.currentTimeMillis(); sendHello() }
            }
        },0,33,TimeUnit.MILLISECONDS)
    }

    private fun sendHello() = sendJson(JSONObject().put("type","hello").put("version",1).put("code",pairingCode))
    private fun sendState() {
        val b: List<String>; val a: Map<String,Double>
        synchronized(lock) { b=pressed.toList(); a=axes.toMap() }
        val aj=JSONObject(); a.forEach { (k,v)->aj.put(k,v) }
        sendJson(JSONObject().put("type","input").put("version",1).put("buttons",JSONArray(b)).put("axes",aj).put("code",pairingCode))
    }
    private fun sendJson(json: JSONObject) {
        val bytes=json.toString().toByteArray(Charsets.UTF_8)
        try { val address=InetAddress.getByName(host); socket?.let { it.send(DatagramPacket(bytes,bytes.size,address,port)) } } catch (_: Exception) { }
    }
    private fun disconnect(message: String?) {
        running=false; connected=false; rejectedByServer=false; sender?.shutdownNow(); sender=null; socket?.close(); socket=null
        synchronized(lock) { pressed.clear(); axes.keys.forEach { axes[it]=0.0 } }
        if (message!=null && ::status.isInitialized) { status.text="● "+message; status.setTextColor(Color.rgb(255,190,90)); connectButton.text="CONECTAR" }
    }
    @Suppress("DEPRECATION")
    private fun vibrateTap() {
        if (!haptics) return
        try {
            val vibrator: Vibrator = if (Build.VERSION.SDK_INT>=31) getSystemService(VibratorManager::class.java).defaultVibrator else getSystemService(VIBRATOR_SERVICE) as Vibrator
            if (Build.VERSION.SDK_INT>=26) vibrator.vibrate(VibrationEffect.createOneShot(18,65)) else vibrator.vibrate(18)
        } catch (_: Exception) { }
    }
    override fun onDestroy() { disconnect(null); super.onDestroy() }
}
