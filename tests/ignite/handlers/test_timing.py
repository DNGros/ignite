import time

from ignite.engine import Events
from ignite.evaluator import Evaluator
from ignite.handlers import Timer
from ignite.trainer import Trainer


def test_timer():
    sleep_t = 0.2
    n_iter = 3

    def _train_func(batch):
        time.sleep(sleep_t)

    def _test_func(batch):
        time.sleep(sleep_t)

    trainer = Trainer(_train_func)
    tester = Evaluator(_test_func)

    t_total = Timer()
    t_batch = Timer(average=True)
    t_train = Timer()

    t_total.attach(trainer)
    t_batch.attach(trainer,
                   pause=Events.ITERATION_COMPLETED,
                   resume=Events.ITERATION_STARTED,
                   step=Events.ITERATION_COMPLETED)
    t_train.attach(trainer,
                   pause=Events.EPOCH_COMPLETED,
                   resume=Events.EPOCH_STARTED)

    @trainer.on(Events.EPOCH_COMPLETED)
    def run_validation(trainer, state):
        tester.run(range(n_iter))

    # Run "training"
    trainer.run(range(n_iter))

    def _equal(lhs, rhs):
        return round(lhs, 1) == round(rhs, 1)

    assert _equal(t_total.value(), (2 * n_iter * sleep_t))
    assert _equal(t_batch.value(), (sleep_t))
    assert _equal(t_train.value(), (n_iter * sleep_t))

    t_total.reset()
    assert _equal(t_total.value(), 0.0)
