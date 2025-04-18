import time

from src.char.BaseChar import BaseChar, Priority


class Camellya(BaseChar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_heavy = 0

    def do_get_switch_priority(self, current_char: BaseChar, has_intro=False, target_low_con=False):
        if has_intro:
            return Priority.MAX - 1
        else:
            return super().do_get_switch_priority(current_char, has_intro)

    def wait_resonance_not_gray(self, timeout=5):
        start = time.time()
        while self.current_resonance() == 0:
            self.click()
            self.sleep(0.1)
            if time.time() - start > timeout:
                self.logger.error('wait wait_resonance_not_gray timed out')

    def on_combat_end(self, chars):
        next_char = str((self.index + 1) % len(chars) + 1)
        self.logger.debug(f'Camellya on_combat_end {self.index} switch next char: {next_char}')
        start = time.time()
        while time.time() - start < 6:
            self.task.load_chars()
            current_char = self.task.get_current_char(raise_exception=False)
            if current_char and current_char.name != "Camellya":
                break
            else:
                self.task.send_key(next_char)
            self.sleep(0.2, False)
        self.logger.debug(f'Camellya on_combat_end {self.index} switch end')

    def do_perform(self):
        if self.has_intro:
            self.continues_normal_attack(1.2)
        self.click_liberation(con_less_than=1)
        start_con = self.get_current_con()
        if start_con < 0.82:
            loop_time = 1.1
        else:
            loop_time = 4.1
        budding_start_time = time.time()
        budding = False
        full = False
        while time.time() - budding_start_time < loop_time or self.task.find_one('camellya_budding', threshold=0.7):
            current_con = self.get_current_con()
            if (start_con - current_con > 0.1) and not budding:
                self.logger.info(f'confull start budding {current_con}')
                budding_start_time = time.time()
                loop_time = 5.1
                budding = True
            elif current_con == 1 and not budding and not full:
                full = True
                loop_time = 1
                budding_start_time = time.time()
            start_con = current_con
            if self.click_resonance(send_click=False)[0]:
                if self.get_current_con() < 0.82 and not budding:
                    self.click_echo()
                    return self.switch_next_char()
                if budding:
                    self.click_liberation()
            else:
                self.click(interval=0.1)
            self.task.next_frame()
            self.check_combat()
        if budding:
            self.click_resonance()
        self.click_echo()
        self.switch_next_char()

    def click_echo(self, *args):
        if self.echo_available():
            self.send_echo_key()
            return True

