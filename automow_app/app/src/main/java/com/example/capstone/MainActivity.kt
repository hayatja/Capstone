package com.example.capstone

import android.annotation.SuppressLint
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.ImageButton
import android.widget.TextView
import androidx.core.view.isVisible

class MainActivity : AppCompatActivity() {
    private var currentState: State = State.STOPPED // State variable
    private var currentTime: Int = 0 // Timer variable
    private var isRunning: Boolean = false // Timer status variable

    private var maxProcessTime: Int = 60; // Total mowing time

    private lateinit var timeHandler: Handler

    private lateinit var startButton: ImageButton
    private lateinit var stopButton: ImageButton
    private lateinit var pauseButton: ImageButton
    private lateinit var statusText: TextView
    private lateinit var timerText: TextView

    private val updateTimer = object : Runnable {
        override fun run() {
            tickTime()
            timeHandler.postDelayed(this, 1000)
        }
    }

    private fun setVisibilityStates() {
        if (currentState == State.STOPPED || currentState == State.PAUSED) {
            startButton.isVisible = true
            stopButton.isVisible = false
            pauseButton.isVisible = false
        } else if (currentState == State.RUNNING) {
            startButton.isVisible = false
            stopButton.isVisible = true
            pauseButton.isVisible = true
        }

        statusText.text = currentState.message
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Add listener on action buttons to detect user input
        startButton = findViewById(R.id.start_button)
        stopButton = findViewById(R.id.stop_button)
        pauseButton = findViewById(R.id.pause_button)

        // Status text element
        statusText = findViewById(R.id.status_text)
        timerText = findViewById(R.id.timer_text)

        // Initial visibility status
        setVisibilityStates()

        startButton.setOnClickListener {
            currentState = State.RUNNING

            // Code to be used when using a single button for all operations
            // startButton.text = getString(R.string.stop)
            // startButton.setBackgroundColor(Color.WHITE)

            setVisibilityStates()

            if (currentTime <= 0) {
                currentTime = maxProcessTime
            }

            isRunning = true
            updateTimeText()
        }

        stopButton.setOnClickListener {
            currentState = State.STOPPED
            setVisibilityStates()

            currentTime = 0
            isRunning = false
            updateTimeText()
        }

        pauseButton.setOnClickListener {
            currentState = State.PAUSED
            setVisibilityStates()

            isRunning = false
        }

        timeHandler = Handler(Looper.getMainLooper())
    }

    override fun onPause() {
        super.onPause()
        timeHandler.removeCallbacks(updateTimer)
    }

    override fun onResume() {
        super.onResume()
        timeHandler.post(updateTimer)
    }

    fun tickTime() {
        if (currentTime > 0 && isRunning) {
            currentTime -= 1
            updateTimeText()
        }

        if (currentTime <= 0 && isRunning) {
            currentState = State.STOPPED
            setVisibilityStates()

            isRunning = false
        }
    }

    @SuppressLint("SetTextI18n")
    fun updateTimeText() {
        val minutes: String = "%02d".format((currentTime / 60))
        val seconds: String = "%02d".format((currentTime % 60))
        timerText.text = "$minutes:$seconds"
    }
}
