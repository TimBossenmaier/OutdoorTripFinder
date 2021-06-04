import {Component, Input, OnInit} from '@angular/core';
import {AbstractControl} from '@angular/forms';

@Component({
  selector: 'tf-form-messages',
  templateUrl: './form-messages.component.html',
  styleUrls: ['./form-messages.component.css']
})
export class FormMessagesComponent implements OnInit {

  @Input() control: AbstractControl;
  @Input() controlName: string;

  private allMessages = {
    name: {
      required: 'Der Tour muss ein Namen gegeben werden.'
    },
    activity_type: {
      required: 'Es mus der Typ der Tour angegeben werden.'
    },
    source: {
      required: 'Es muss die Quelle des Informaterials angegeben werden (bspw. Outdoor 03 2020)'
    },
    save_path: {
      required: 'Es muss der Speicherort des Infomaterials angegeben werden.'
    },
    multi_day: {
      required: 'Länge der Tour muss angegben werden.',
      minLength: 'Es dürfen nur die Werte true und false verwendet werden.',
      maxLength: 'Es dürfen nur die Werte true und false verwendet werden.'
    },
    locations: {
      required: 'Es muss ein Ort angegeben werden.'
    }
  };
  constructor() { }

  ngOnInit(): void {
  }

  errorsForControl(): string[] {
    const messages = this.allMessages[this.controlName];

    if (
      !this.control ||
      !this.control.errors ||
      !messages ||
      !this.control.dirty
    ) {return null; }

    return Object.keys(this.control.errors).map(err => messages[err]);
  }

}
