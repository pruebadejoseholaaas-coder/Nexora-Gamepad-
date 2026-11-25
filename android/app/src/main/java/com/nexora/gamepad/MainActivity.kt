package com.nexora.gamepad

import android.app.Activity
import android.os.Bundle
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.view.Gravity
import android.view.MotionEvent
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import org.json.JSONArray
import org.json.JSONObject
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import kotlin.concurrent.thread

class MainActivity : Activity() {
    private var socket: DatagramSocket? = null
    private var host = "192.168.1.100"
    private val port = 26760
    private val pressed = mutableSetOf<String>()
    private lateinit var status: TextView
    private lateinit var ipField: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.decorView.systemUiVisibility =
            5894 or 1024 or 512 or 4096

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(18, 12, 18, 12)
            setBackgroundColor(0xFF10131B.toInt())
        }

        val title = TextView(this).apply {
            text = "NEXORA GAMEPAD"
            textSize = 24f
            setTextColor(0xFFFFFFFF.toInt())
            gravity = Gravity.CENTER
        }
        root.addView(title)

        val connection = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        ipField = EditText(this).apply {
            setSingleLine(true)
            setText(host)
            hint = "IP local de tu PC"
            setTextColor(0xFFFFFFFF.toInt())
            setHintTextColor(0xFFAAAAAA.toInt())
        }
        connection.addView(ipField, LinearLayout.LayoutParams(0, 52, 1f))
        val connect = Button(this).apply {
            text = "Conectar"
            setOnClickListener {
                host = ipField.text.toString().trim()
                status.text = "Destino: $host:$port"
                sendState()
            }
        }
        connection.addView(connect)
        root.addView(connection)

        status = TextView(this).apply {
            text = "Introduce la IP local que muestra Nexora en Windows"
            textSize = 13f
            setTextColor(0xFFB9C3D5.toInt())
            gravity = Gravity.CENTER
        }
        root.addView(status)

        val controls = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
        }
        val dpad = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
        }
        dpad.addView(controlButton("↑", "UP"))
        val horizontal = LinearLayout(this).apply { gravity = Gravity.CENTER }
        horizontal.addView(controlButton("←", "LEFT"))
        horizontal.addView(controlButton("↓", "DOWN"))
        horizontal.addView(controlButton("→", "RIGHT"))
        dpad.addView(horizontal)
        controls.addView(dpad, LinearLayout.LayoutParams(0, 220, 1f))

        val actions = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
        }
        val top = LinearLayout(this).apply { gravity = Gravity.CENTER }
        top.addView(controlButton("Y", "Y"))
        top.addView(controlButton("X", "X"))
        actions.addView(top)
        val bottom = LinearLayout(this).apply { gravity = Gravity.CENTER }
        bottom.addView(controlButton("B", "B"))
        bottom.addView(controlButton("A", "A"))
        actions.addView(bottom)
        controls.addView(actions, LinearLayout.LayoutParams(0, 220, 1f))
        root.addView(controls)

        val note = TextView(this).apply {
            text = "MVP inicial • Wi-Fi local • Vibración táctil del teléfono"
            textSize = 12f
            setTextColor(0xFF8E9AAF.toInt())
            gravity = Gravity.CENTER
        }
        root.addView(note)
        setContentView(root)
    }

    private fun controlButton(label: String, key: String): Button {
        return Button(this).apply {
            text = label
            textSize = 18f
            setOnTouchListener { _, event ->
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        pressed.add(key)
                        vibrateTap()
                        sendState()
                        true
                    }
                    MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                        pressed.remove(key)
                        sendState()
                        true
                    }
                    else -> true
                }
            }
        }
    }

    private fun vibrateTap() {
        try {
            val vibrator = if (Build.VERSION.SDK_INT >= 31) {
                getSystemService(VibratorManager::class.java).defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                getSystemService(VIBRATOR_SERVICE) as Vibrator
            }
            if (Build.VERSION.SDK_INT >= 26) {
                vibrator.vibrate(VibrationEffect.createOneShot(18, 70))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(18)
            }
        } catch (_: Exception) { }
    }

    private fun sendState() {
        val packet = JSONObject().apply {
            put("type", "input")
            put("version", 1)
            put("buttons", JSONArray(pressed.toList()))
            put("axes", JSONObject().apply {
                put("leftX", 0.0); put("leftY", 0.0)
                put("rightX", 0.0); put("rightY", 0.0)
                put("leftTrigger", 0.0); put("rightTrigger", 0.0)
            })
        }.toString().toByteArray(Charsets.UTF_8)

        thread {
            try {
                if (socket == null || socket!!.isClosed) socket = DatagramSocket()
                val address = InetAddress.getByName(host)
                socket!!.send(DatagramPacket(packet, packet.size, address, port))
            } catch (e: Exception) {
                runOnUiThread { status.text = "No se pudo enviar: revisa la IP y el Wi-Fi" }
            }
        }
    }

    override fun onDestroy() {
        socket?.close()
        super.onDestroy()
    }
}
