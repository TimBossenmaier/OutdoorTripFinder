import {Component, Input, OnDestroy, OnInit} from '@angular/core';
import {Subscription} from 'rxjs';
import {NavigationStart, Router} from '@angular/router';
import {Alert, AlertType} from '../shared/alert';
import {AlertService} from '../shared/alert.service';

@Component({
  selector: 'tf-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.css']
})
export class AlertComponent implements OnInit, OnDestroy {

  @Input() id = 'default-alert';
  @Input() fade = true;

  alerts: Alert[] = [];
  alertSubscription: Subscription;
  routeSubscription: Subscription;

  constructor(
    private router: Router,
    private als: AlertService
  ) { }

  ngOnInit(): void {
    // subscribe to new alert notification
    this.alertSubscription = this.als.onAlert(this.id)
      .subscribe(alert => {
        // clear alerts when an empty alert is received
        if (!alert.message) {
          // filter out alters without 'keepAfterRouteChange' flag
          this.alerts = this.alerts.filter(x => x.keepAfterRouteChange);

          // remove flag
          this.alerts.forEach( x => delete x.keepAfterRouteChange);
          return;
      }
      // add alert to array
        this.alerts.push(alert);

      // auto close alert if required
        if (alert.autoClose) {
        setTimeout(() => this.removeAlert(alert), 3000);
      }
      });

    // clear alerts on location change
    this.routeSubscription = this.router.events.subscribe(event => {
      if (event instanceof NavigationStart) {
        this.als.clear(this.id);
      }
    });
  }

  ngOnDestroy() {
    // unsubscribe to avoid memory leaks
    this.alertSubscription.unsubscribe();
    this.routeSubscription.unsubscribe();
  }

  removeAlert(alert: Alert){
    // check if already removed
    if (!this.alerts.includes(alert)) { return; }

    if (this.fade) {
      alert.fade = true;

      // remove after faded out
      setTimeout(() => {
        this.alerts = this.alerts.filter(x => x !== alert);
      }, 250);
    } else {
      // remove alert
      this.alerts = this.alerts.filter(x => x !== alert);
    }
  }

  cssClass(alert: Alert) {
    if (!alert) { return; }

    const classes = ['alert', 'alert-dismissable', 'mt-4', 'container'];

    const alertTypeClass = {
      [AlertType.Success]: 'ui success message',
      [AlertType.Error]: 'ui negative message',
      [AlertType.Info]: 'ui info message',
      [AlertType.Warning]: 'ui warning message'
    };

    classes.push(alertTypeClass[alert.type]);

    if (alert.fade) {
      classes.push('fade');
    }

    return classes.join(' ');
  }
}
