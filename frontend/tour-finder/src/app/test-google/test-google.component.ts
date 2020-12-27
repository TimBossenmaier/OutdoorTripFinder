import { Component, ViewChild, EventEmitter, Output, OnInit, AfterViewInit, Input} from '@angular/core';
import { FormGroup, FormBuilder} from '@angular/forms';
import {} from 'googlemaps';


// TODO: custom styling https://developers.google.com/maps/documentation/javascript/places-autocomplete#place_autocomplete_service
@Component({
  // tslint:disable-next-line:component-selector
  selector: 'TestGoogleComponent',
  template: `
  <input class="input" type="text"
  #addresstext style="padding: 12px 20px; border: 1Px solid #ccc; width: 400px;">`, })

export class TestGoogleComponent implements OnInit, AfterViewInit {
  @Input() addressType: string;
  @Output() coordinates = new EventEmitter<any>();
  @ViewChild('addresstext') addresstext: any;

  autoCompleteInput: string;
  queryWait: boolean;

  constructor() {
  }

  ngOnInit() {
  }

  ngAfterViewInit() {
     this.getPlaceAutocomplete();
  }

  private getPlaceAutocomplete() {
    const auto = new google.maps.places.Autocomplete(this.addresstext.nativeElement, {
      types: [this.addressType]
    });
    google.maps.event.addListener(auto, 'place_changed', () => {
      const place = auto.getPlace();
      this.coordinates.emit({long: place.geometry.location.lng(), lat: place.geometry.location.lat()});
    });
  }

}
