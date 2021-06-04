import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {FormControl, FormControlName} from '@angular/forms';
import {map, startWith} from 'rxjs/operators';

@Component({
  selector: 'tf-custom-autocomplete',
  templateUrl: './custom-autocomplete.component.html',
  styleUrls: ['./custom-autocomplete.component.css']
})
export class CustomAutocompleteComponent implements OnInit {

  @Input() myControl: FormControl;
  @Input() items: string[];
  filteredOptions: Observable<string[]>;

  constructor() { }

  ngOnInit(): void {
    this.filteredOptions = this.myControl.valueChanges.pipe(
      startWith(''), map(value => this._filter(value))
    );
  }

  private _filter(value: string): string[] {
    const filterValue = value.toLowerCase();

    return this.items.filter(item => item.toLowerCase().indexOf(filterValue) === 0);
  }

}
