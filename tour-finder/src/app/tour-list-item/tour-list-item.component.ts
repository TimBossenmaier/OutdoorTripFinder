import {Component, Input, OnInit} from '@angular/core';
import {Tour} from '../shared/tour';

@Component({
  selector: 'tf-tour-list-item',
  templateUrl: './tour-list-item.component.html',
  styleUrls: ['./tour-list-item.component.css']
})
export class TourListItemComponent implements OnInit {
@Input() tour: Tour;

  constructor() { }

  ngOnInit(): void {
  }

}
