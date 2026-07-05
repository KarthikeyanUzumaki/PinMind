import React from 'react';
import { motion } from 'framer-motion';

const promptGroups = [
  {
    category: 'GPIO',
    prompts: [
      { label: 'Blink LED', text: 'Configure GPIO pin for LED blink' },
      { label: 'Button Interrupt', text: 'Set up GPIO input pin with falling edge interrupt for a button' },
    ]
  },
  {
    category: 'Communication',
    prompts: [
      { label: 'UART Echo', text: 'Configure UART peripheral at 115200 baud for echo communication' },
      { label: 'I2C Scan', text: 'Write I2C scanner to detect peripheral addresses on the bus' },
    ]
  },
  {
    category: 'Sensors',
    prompts: [
      { label: 'ADC Read', text: 'Initialize ADC channel to read analog voltage from a sensor' },
      { label: 'DHT11 Temp', text: 'Read temperature and humidity from DHT11 sensor' },
    ]
  },
  {
    category: 'Motor',
    prompts: [
      { label: 'PWM Servo', text: 'Configure PWM signal to control a SG90 servo motor' },
      { label: 'DC Motor Speed', text: 'Initialize PWM and direction pins for DC motor controller' },
    ]
  }
];

export default function QuickPromptBar({ onSelect }) {
  return (
    <div className="flex flex-col gap-2 my-2 w-full">
      <div className="text-[10px] uppercase font-mono-editor tracking-wider" style={{ color: 'var(--pm-text-muted)' }}>
        Quick Prompts
      </div>
      <div className="flex flex-wrap gap-3">
        {promptGroups.map((group) => (
          <div key={group.category} className="flex flex-col gap-1 bg-[var(--pm-surface-2)] p-2 rounded-lg border border-[var(--pm-border)]">
            <span className="text-[9px] font-bold" style={{ color: 'var(--accent)' }}>{group.category}</span>
            <div className="flex gap-1.5">
              {group.prompts.map((prompt) => (
                <button
                  key={prompt.label}
                  onClick={() => onSelect(prompt.text)}
                  className="text-[10px] px-2 py-1 rounded bg-[var(--pm-surface-3)] hover:bg-[var(--accent-dim)] hover:text-[var(--accent)] transition-colors cursor-pointer border border-[var(--pm-border-2)]"
                  style={{ color: 'var(--pm-text)' }}
                >
                  {prompt.label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
